from __future__ import annotations

import sqlite3

from .db import fetch_all, fetch_one, scalar

LANDING_FACTS_SQL = """
SELECT
    (SELECT MIN(YearID) FROM YearDate) AS min_year,
    (SELECT MAX(YearID) FROM YearDate) AS max_year,
    (SELECT COUNT(*) FROM Country) AS country_count,
    (SELECT COUNT(*) FROM Antigen) AS antigen_count,
    (SELECT COUNT(*) FROM Infection_Type) AS infection_type_count,
    (SELECT ROUND(SUM(CAST(NULLIF(doses, '') AS REAL))) FROM Vaccination WHERE NULLIF(doses, '') IS NOT NULL) AS total_doses,
    (SELECT ROUND(SUM(cases)) FROM InfectionData) AS total_cases
"""

LANDING_OVERVIEW_SQL = """
SELECT
    it.description AS label,
    SUM(i.cases) AS total_cases
FROM InfectionData i
JOIN Infection_Type it ON it.id = i.inf_type
GROUP BY it.description
ORDER BY total_cases DESC, it.description ASC
"""

PERSONAS_SQL = """
SELECT slug, name, headline, demographic, needs, goals, skills, pain_points, image_path
FROM Persona
ORDER BY display_order ASC, name ASC
"""

TEAM_MEMBERS_SQL = """
SELECT full_name, student_number, role_label
FROM TeamMember
ORDER BY display_order ASC, full_name ASC
"""

LOOKUP_SQLS = {
    "years": "SELECT YearID AS value, CAST(YearID AS TEXT) AS label FROM YearDate ORDER BY YearID ASC",
    "antigens": "SELECT AntigenID AS value, name AS label FROM Antigen ORDER BY AntigenID ASC",
    "infection_types": "SELECT id AS value, description AS label FROM Infection_Type ORDER BY description ASC",
    "economies": "SELECT CAST(economyID AS TEXT) AS value, phase AS label FROM Economy ORDER BY economyID ASC",
    "regions": "SELECT RegionID AS value, region AS label FROM Region ORDER BY region ASC",
    "countries": "SELECT CountryID AS value, name AS label FROM Country ORDER BY name ASC",
}

VACCINATION_RATE_SORTS = {
    "coverage_desc": "coverage_pct DESC, country_name ASC",
    "coverage_asc": "coverage_pct ASC, country_name ASC",
    "country_asc": "country_name ASC",
    "country_desc": "country_name DESC",
    "region_asc": "region_name ASC, country_name ASC",
    "region_desc": "region_name DESC, country_name ASC",
}

INFECTION_ECONOMY_SORTS = {
    "cases_per_100k_desc": "cases_per_100k DESC, country_name ASC",
    "cases_per_100k_asc": "cases_per_100k ASC, country_name ASC",
    "cases_desc": "raw_cases DESC, country_name ASC",
    "cases_asc": "raw_cases ASC, country_name ASC",
    "country_asc": "country_name ASC",
    "country_desc": "country_name DESC",
}

VACCINATION_IMPROVEMENT_SORTS = {
    "increase_desc": "rate_increase DESC, country_name ASC",
    "increase_asc": "rate_increase ASC, country_name ASC",
    "country_asc": "country_name ASC",
    "country_desc": "country_name DESC",
}

ABOVE_AVERAGE_SORTS = {
    "rate_desc": "cases_per_100k DESC, country_name ASC",
    "rate_asc": "cases_per_100k ASC, country_name ASC",
    "country_asc": "country_name ASC",
    "country_desc": "country_name DESC",
}


def fetch_lookups(conn: sqlite3.Connection) -> dict[str, list[dict[str, str]]]:
    lookups: dict[str, list[dict[str, str]]] = {}
    for name, sql in LOOKUP_SQLS.items():
        lookups[name] = [
            {"value": str(row["value"]), "label": str(row["label"])}
            for row in fetch_all(conn, sql)
        ]
    return lookups


def fetch_landing_facts(conn: sqlite3.Connection) -> dict[str, float | int]:
    row = fetch_one(conn, LANDING_FACTS_SQL)
    if row is None:
        return {}
    return dict(row)


def fetch_landing_overview(conn: sqlite3.Connection) -> list[dict[str, float | str]]:
    return [dict(row) for row in fetch_all(conn, LANDING_OVERVIEW_SQL)]


def fetch_personas(conn: sqlite3.Connection) -> list[dict[str, str]]:
    return [dict(row) for row in fetch_all(conn, PERSONAS_SQL)]


def fetch_team_members(conn: sqlite3.Connection) -> list[dict[str, str]]:
    return [dict(row) for row in fetch_all(conn, TEAM_MEMBERS_SQL)]


def fetch_vaccination_rates(
    conn: sqlite3.Connection,
    antigen: str,
    year: int,
    region: str,
    country: str,
    sort_key: str,
) -> dict[str, list[dict[str, object]]]:
    sort_sql = VACCINATION_RATE_SORTS[sort_key]
    country_rows = fetch_all(
        conn,
        f"""
        SELECT
            v.antigen,
            v.year,
            c.CountryID AS country_code,
            c.name AS country_name,
            r.region AS region_name,
            ROUND(CAST(NULLIF(v.coverage, '') AS REAL), 2) AS coverage_pct
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        JOIN Region r ON r.RegionID = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND CAST(NULLIF(v.coverage, '') AS REAL) >= 90
          AND (? = '' OR c.region = ?)
          AND (? = '' OR c.CountryID = ?)
        ORDER BY {sort_sql}
        """,
        (antigen, year, region, region, country, country),
    )
    region_rows = fetch_all(
        conn,
        """
        SELECT
            r.RegionID AS region_code,
            r.region AS region_name,
            COUNT(*) AS countries_meeting_target
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        JOIN Region r ON r.RegionID = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND CAST(NULLIF(v.coverage, '') AS REAL) >= 90
          AND (? = '' OR c.region = ?)
        GROUP BY r.RegionID, r.region
        ORDER BY countries_meeting_target DESC, r.region ASC
        """,
        (antigen, year, region, region),
    )
    excluded_count = scalar(
        conn,
        """
        SELECT COUNT(*)
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        WHERE v.antigen = ?
          AND v.year = ?
          AND NULLIF(v.coverage, '') IS NULL
          AND (? = '' OR c.region = ?)
          AND (? = '' OR c.CountryID = ?)
        """,
        (antigen, year, region, region, country, country),
    )
    return {
        "country_rows": [dict(row) for row in country_rows],
        "region_rows": [dict(row) for row in region_rows],
        "excluded_count": int(excluded_count or 0),
    }


def fetch_infection_by_economy(
    conn: sqlite3.Connection,
    economy: int,
    infection: str,
    year: int,
    sort_key: str,
) -> dict[str, list[dict[str, object]]]:
    sort_sql = INFECTION_ECONOMY_SORTS[sort_key]
    country_rows = fetch_all(
        conn,
        f"""
        SELECT
            it.description AS infection_name,
            c.name AS country_name,
            e.phase AS economic_phase,
            i.year,
            ROUND(i.cases, 0) AS raw_cases,
            ROUND(i.cases * 100000.0 / p.population, 2) AS cases_per_100k
        FROM InfectionData i
        JOIN Infection_Type it ON it.id = i.inf_type
        JOIN Country c ON c.CountryID = i.country
        JOIN Economy e ON e.economyID = c.economy
        JOIN CountryPopulation p ON p.country = i.country AND p.year = i.year
        WHERE c.economy = ?
          AND i.inf_type = ?
          AND i.year = ?
        ORDER BY {sort_sql}
        """,
        (economy, infection, year),
    )
    summary_rows = fetch_all(
        conn,
        """
        SELECT
            e.phase AS economic_phase,
            ROUND(SUM(i.cases), 0) AS total_cases
        FROM InfectionData i
        JOIN Country c ON c.CountryID = i.country
        JOIN Economy e ON e.economyID = c.economy
        WHERE i.inf_type = ?
          AND i.year = ?
        GROUP BY e.phase
        ORDER BY total_cases DESC, e.phase ASC
        """,
        (infection, year),
    )
    return {
        "country_rows": [dict(row) for row in country_rows],
        "summary_rows": [dict(row) for row in summary_rows],
    }


def fetch_vaccination_improvement(
    conn: sqlite3.Connection,
    antigen: str,
    start_year: int,
    end_year: int,
    limit: int,
    sort_key: str,
) -> list[dict[str, object]]:
    sort_sql = VACCINATION_IMPROVEMENT_SORTS[sort_key]
    rows = fetch_all(
        conn,
        f"""
        WITH start_data AS (
            SELECT
                v.country,
                v.inf_type,
                v.antigen,
                c.name AS country_name,
                CAST(NULLIF(v.doses, '') AS REAL) AS start_doses,
                p.population AS start_population
            FROM Vaccination v
            JOIN CountryPopulation p ON p.country = v.country AND p.year = v.year
            JOIN Country c ON c.CountryID = v.country
            WHERE v.antigen = ?
              AND v.year = ?
              AND NULLIF(v.doses, '') IS NOT NULL
        ),
        end_data AS (
            SELECT
                v.country,
                v.inf_type,
                v.antigen,
                CAST(NULLIF(v.doses, '') AS REAL) AS end_doses,
                p.population AS end_population
            FROM Vaccination v
            JOIN CountryPopulation p ON p.country = v.country AND p.year = v.year
            WHERE v.antigen = ?
              AND v.year = ?
              AND NULLIF(v.doses, '') IS NOT NULL
        )
        SELECT
            s.country_name,
            ROUND((e.end_doses * 100.0 / e.end_population) - (s.start_doses * 100.0 / s.start_population), 2) AS rate_increase,
            ? AS start_year,
            ? AS end_year
        FROM start_data s
        JOIN end_data e
          ON e.country = s.country
         AND e.inf_type = s.inf_type
         AND e.antigen = s.antigen
        ORDER BY {sort_sql}
        LIMIT ?
        """,
        (antigen, start_year, antigen, end_year, start_year, end_year, limit),
    )
    return [dict(row) for row in rows]


def fetch_above_average_infection(
    conn: sqlite3.Connection,
    infection: str,
    year: int,
    sort_key: str,
) -> dict[str, object]:
    sort_sql = ABOVE_AVERAGE_SORTS[sort_key]
    rows = fetch_all(
        conn,
        f"""
        WITH country_rates AS (
            SELECT
                c.name AS country_name,
                i.cases AS raw_cases,
                p.population,
                (i.cases * 100000.0 / p.population) AS cases_per_100k
            FROM InfectionData i
            JOIN CountryPopulation p ON p.country = i.country AND p.year = i.year
            JOIN Country c ON c.CountryID = i.country
            WHERE i.inf_type = ?
              AND i.year = ?
        ),
        global_rate AS (
            SELECT (SUM(raw_cases) * 100000.0 / SUM(population)) AS global_cases_per_100k
            FROM country_rates
        )
        SELECT
            country_name,
            ROUND(cases_per_100k, 2) AS cases_per_100k,
            ROUND((SELECT global_cases_per_100k FROM global_rate), 2) AS global_cases_per_100k
        FROM country_rates
        WHERE cases_per_100k > (SELECT global_cases_per_100k FROM global_rate)
        ORDER BY {sort_sql}
        """,
        (infection, year),
    )
    global_row = fetch_one(
        conn,
        """
        WITH country_rates AS (
            SELECT
                i.cases AS raw_cases,
                p.population
            FROM InfectionData i
            JOIN CountryPopulation p ON p.country = i.country AND p.year = i.year
            WHERE i.inf_type = ?
              AND i.year = ?
        )
        SELECT ROUND((SUM(raw_cases) * 100000.0 / SUM(population)), 2) AS global_cases_per_100k
        FROM country_rates
        """,
        (infection, year),
    )
    return {
        "global_rate": 0 if global_row is None else float(global_row["global_cases_per_100k"]),
        "rows": [dict(row) for row in rows],
    }
