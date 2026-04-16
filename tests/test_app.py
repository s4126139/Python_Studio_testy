from __future__ import annotations

import shutil
import sqlite3
import tempfile
import threading
import time
import unittest
from contextlib import closing
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from wsgiref.simple_server import make_server

from pid_app.app import create_app
from pid_app.bootstrap import ensure_app_db
from pid_app.queries import fetch_above_average_infection, fetch_vaccination_improvement


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DB = ROOT / "immunisation (1).db"


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_creates_working_db_without_mutating_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            source_copy = temp_dir / SOURCE_DB.name
            app_db = temp_dir / "app.db"
            shutil.copyfile(SOURCE_DB, source_copy)
            before_size = source_copy.stat().st_size

            result_path = ensure_app_db(source_db=source_copy, app_db=app_db)

            self.assertEqual(result_path, app_db)
            self.assertTrue(app_db.exists())
            self.assertEqual(source_copy.stat().st_size, before_size)

            with closing(sqlite3.connect(app_db)) as conn:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Persona', 'TeamMember')"
                    )
                }
                self.assertEqual(tables, {"Persona", "TeamMember"})
                persona_count = conn.execute("SELECT COUNT(*) FROM Persona").fetchone()[0]
                team_count = conn.execute("SELECT COUNT(*) FROM TeamMember").fetchone()[0]

            self.assertGreaterEqual(persona_count, 2)
            self.assertGreaterEqual(team_count, 2)

    def test_blank_vaccination_values_are_ignored_in_queries(self) -> None:
        with closing(sqlite3.connect(SOURCE_DB)) as conn:
            blank_count = conn.execute("SELECT COUNT(*) FROM Vaccination WHERE coverage = ''").fetchone()[0]
            qualifying_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM Vaccination
                WHERE antigen = 'MCV2'
                  AND year = 2010
                  AND CAST(NULLIF(coverage, '') AS REAL) >= 90
                """
            ).fetchone()[0]

        self.assertGreater(blank_count, 0)
        self.assertGreater(qualifying_count, 0)


class QueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)
        self.source_db = temp_path / SOURCE_DB.name
        self.app_db = temp_path / "app.db"
        shutil.copyfile(SOURCE_DB, self.source_db)
        ensure_app_db(source_db=self.source_db, app_db=self.app_db)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_vaccination_improvement_uses_population_rate_math(self) -> None:
        with closing(sqlite3.connect(self.app_db)) as conn:
            conn.row_factory = sqlite3.Row
            rows = fetch_vaccination_improvement(conn, "MCV1", 2000, 2024, 10, "increase_desc")
            self.assertTrue(rows)
            top_row = rows[0]
            self.assertIn("rate_increase", top_row)
            self.assertGreater(float(top_row["rate_increase"]), 0.0)

    def test_above_average_rows_exceed_global_rate(self) -> None:
        with closing(sqlite3.connect(self.app_db)) as conn:
            conn.row_factory = sqlite3.Row
            data = fetch_above_average_infection(conn, "MEA", 2020, "rate_desc")

        self.assertGreater(data["global_rate"], 0.0)
        self.assertTrue(data["rows"])
        self.assertTrue(all(float(row["cases_per_100k"]) > float(data["global_rate"]) for row in data["rows"]))


class HttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)
        self.source_db = temp_path / SOURCE_DB.name
        self.app_db = temp_path / "app.db"
        shutil.copyfile(SOURCE_DB, self.source_db)

        self.application = create_app(source_db=self.source_db, app_db=self.app_db)
        self.server = make_server("127.0.0.1", 0, self.application)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)
        self.temp_dir.cleanup()

    def fetch(self, path: str) -> str:
        with urlopen(f"http://127.0.0.1:{self.port}{path}") as response:
            return response.read().decode("utf-8")

    def test_all_primary_routes_return_200(self) -> None:
        routes = [
            ("/", "Preventable Infectious Diseases Atlas"),
            ("/mission", "Why this atlas exists"),
            ("/vaccination-rates", "Vaccination rates by country and region"),
            ("/infection-by-economy", "Infection data by economic status"),
            ("/vaccination-improvement", "Biggest improvement in vaccination rate"),
            ("/above-average-infection", "Countries above the global infection rate"),
        ]
        for path, marker in routes:
            with self.subTest(path=path):
                html = self.fetch(path)
                self.assertIn(marker, html)

    def test_chart_markup_is_present_on_data_routes(self) -> None:
        for path in [
            "/",
            "/vaccination-rates",
            "/infection-by-economy",
            "/vaccination-improvement",
            "/above-average-infection",
        ]:
            with self.subTest(path=path):
                html = self.fetch(path)
                self.assertIn('class="chart-image"', html)

    def test_invalid_params_render_inline_message(self) -> None:
        html = self.fetch("/vaccination-improvement?start_year=2024&end_year=2020")
        self.assertIn("The start year must be earlier than the end year.", html)

        html = self.fetch("/vaccination-rates?year=3000&sort=unknown")
        self.assertIn("Year was not recognised", html)
        self.assertIn("Sort order was not recognised", html)

    def test_sort_and_filter_inputs_change_results(self) -> None:
        high_to_low = self.fetch("/infection-by-economy?economy=2&infection=MEA&year=2022&sort=cases_per_100k_desc")
        low_to_high = self.fetch("/infection-by-economy?economy=2&infection=MEA&year=2022&sort=cases_per_100k_asc")
        self.assertNotEqual(high_to_low, low_to_high)

    def test_not_found_route_returns_http_error(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.fetch("/missing")
        self.assertEqual(context.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
