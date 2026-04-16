from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs

from .bootstrap import ensure_app_db
from .db import connect
from .queries import (
    ABOVE_AVERAGE_SORTS,
    INFECTION_ECONOMY_SORTS,
    VACCINATION_IMPROVEMENT_SORTS,
    VACCINATION_RATE_SORTS,
    fetch_above_average_infection,
    fetch_infection_by_economy,
    fetch_landing_facts,
    fetch_landing_overview,
    fetch_lookups,
    fetch_personas,
    fetch_team_members,
    fetch_vaccination_improvement,
    fetch_vaccination_rates,
)
from .render import (
    data_table,
    fact_block,
    filter_form,
    format_compact,
    format_number,
    horizontal_bar_chart,
    initials,
    message_html,
    number_field,
    overview_template,
    page_template,
    route_link,
    section,
    select_field,
    sort_field,
    stat_band,
    threshold_chart,
    vertical_bar_chart,
)

BytesResponse = tuple[str, list[tuple[str, str]], bytes]

SITE_NAME = "Preventable Infectious Diseases Atlas"

MISSION_COPY = {
    "statement": "This atlas turns the provided WHO-style immunisation dataset into an explorable public reference. The site keeps a neutral tone, shows what the data can support, and states where missing vaccination values limit interpretation.",
    "how_to_use": [
        "Start on the overview page for the time range, coverage scale, and the routes into deeper analysis.",
        "Use the middle pages to filter by geography, economic status, year, and disease type.",
        "Use the deep-dive pages when you need comparative outliers, rate jumps, or countries above the global rate.",
    ],
}


@dataclass
class AppConfig:
    source_db: Path
    app_db: Path
    static_dir: Path


def create_app(source_db: Path | None = None, app_db: Path | None = None) -> Callable:
    base_dir = Path(__file__).resolve().parent.parent
    config = AppConfig(
        source_db=Path(source_db) if source_db else base_dir / "immunisation (1).db",
        app_db=Path(app_db) if app_db else base_dir / "app.db",
        static_dir=base_dir / "static",
    )
    ensure_app_db(source_db=config.source_db, app_db=config.app_db)

    def application(environ: dict, start_response: Callable) -> list[bytes]:
        response = dispatch_request(config, environ)
        start_response(response[0], response[1])
        return [response[2]]

    return application


def dispatch_request(config: AppConfig, environ: dict) -> BytesResponse:
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method != "GET":
        return html_response("405 Method Not Allowed", "<h1>Method not allowed</h1>")
    if path == "/static/styles.css":
        return serve_css(config.static_dir / "styles.css")

    routes: dict[str, Callable[[AppConfig, dict[str, list[str]]], str]] = {
        "/": handle_overview,
        "/mission": handle_mission,
        "/vaccination-rates": handle_vaccination_rates,
        "/infection-by-economy": handle_infection_by_economy,
        "/vaccination-improvement": handle_vaccination_improvement,
        "/above-average-infection": handle_above_average_infection,
    }
    handler = routes.get(path)
    if handler is None:
        return html_response(
            "404 Not Found",
            page_template(
                "Page not found",
                "",
                '<section class="content-section"><h1>Page not found</h1><p>The requested route does not exist.</p></section>',
            ),
        )

    query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    return html_response("200 OK", handler(config, query))


def html_response(status: str, body: str) -> BytesResponse:
    return status, [("Content-Type", "text/html; charset=utf-8")], body.encode("utf-8")


def serve_css(path: Path) -> BytesResponse:
    return "200 OK", [("Content-Type", "text/css; charset=utf-8")], path.read_bytes()


def first_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key, [""])
    return values[0] if values else ""


def validate_required_choice(
    raw_value: str,
    allowed_values: set[str],
    default_value: str,
    field_label: str,
    messages: list[str],
) -> str:
    if raw_value == "":
        return default_value
    if raw_value not in allowed_values:
        messages.append(f"{field_label} was not recognised, so the default value was used.")
        return default_value
    return raw_value


def validate_optional_choice(
    raw_value: str,
    allowed_values: set[str],
    field_label: str,
    messages: list[str],
) -> str:
    if raw_value == "":
        return ""
    if raw_value not in allowed_values:
        messages.append(f"{field_label} was not recognised, so that filter was cleared.")
        return ""
    return raw_value


def validate_limit(raw_value: str, default_value: int, messages: list[str]) -> int:
    if raw_value == "":
        return default_value
    try:
        value = int(raw_value)
    except ValueError:
        messages.append("The country limit must be a whole number, so the default value was used.")
        return default_value
    if value < 1 or value > 50:
        messages.append("The country limit must stay between 1 and 50, so the default value was used.")
        return default_value
    return value


def handle_overview(config: AppConfig, _query: dict[str, list[str]]) -> str:
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        facts = fetch_landing_facts(conn)
        overview = fetch_landing_overview(conn)

    fact_items = [
        fact_block("Dataset span", f"{facts['min_year']}-{facts['max_year']}", "All pages use the same 25-year window."),
        fact_block("Countries", format_number(facts["country_count"]), "Country and region filters resolve from SQLite lookups."),
        fact_block("Recorded numeric doses", format_compact(facts["total_doses"]), "Blank vaccination dose fields are excluded."),
        fact_block("Reported infection cases", format_compact(facts["total_cases"]), "Cases combine measles, pertussis, and rubella."),
    ]
    overview_chart = vertical_bar_chart(
        [(item["label"], float(item["total_cases"])) for item in overview],
        "Total reported cases by infection type",
    )

    routes = "".join(
        [
            route_link("Mission and audience", "/mission", "Purpose, usage, personas, and team records from the database."),
            route_link("Vaccination rates", "/vaccination-rates", "Find countries and regions meeting 90 percent coverage."),
            route_link("Economic status view", "/infection-by-economy", "Compare infection burden by economic phase."),
            route_link("Vaccination improvement", "/vaccination-improvement", "Measure the biggest rate jump across a chosen period."),
            route_link("Above-average infection", "/above-average-infection", "Surface countries whose infection rate exceeds the global rate."),
        ]
    )

    body = f"""
    <section class="hero">
      <div class="hero-copy">
        <p class="hero-kicker">Global immunisation evidence, rendered from the provided SQLite dataset.</p>
        <h1>{SITE_NAME}</h1>
        <p class="hero-body">
          A server-rendered reference for reading vaccination progress, infection burden, and outlier countries without leaving the underlying data context behind.
        </p>
        <div class="hero-actions">
          <a class="button-primary" href="/vaccination-rates">Start with rates</a>
          <a class="button-secondary" href="/mission">Read the mission</a>
        </div>
      </div>
      <div class="hero-chart">
        {overview_chart}
      </div>
    </section>
    {stat_band(fact_items)}
    <section class="route-grid">
      <div class="route-grid-heading">
        <p class="section-kicker">Six routes, one dataset</p>
        <h2>Choose the level of detail you need</h2>
        <p>Begin with the big picture, then move into filterable and ranked views that stay grounded in raw SQL and server-side Matplotlib output.</p>
      </div>
      <div class="route-grid-links">{routes}</div>
    </section>
    """
    return overview_template(body)


def handle_mission(config: AppConfig, _query: dict[str, list[str]]) -> str:
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        personas = fetch_personas(conn)
        team_members = fetch_team_members(conn)

    persona_markup = []
    for persona in personas:
        avatar = f'<div class="persona-avatar">{escape(initials(persona["name"]))}</div>'
        persona_markup.append(
            f"""
            <article class="persona-panel">
              {avatar}
              <div class="persona-content">
                <h3>{escape(persona["name"])}</h3>
                <p class="persona-headline">{escape(persona["headline"])}</p>
                <dl class="persona-grid">
                  <div><dt>Demographic</dt><dd>{escape(persona["demographic"])}</dd></div>
                  <div><dt>Needs</dt><dd>{escape(persona["needs"])}</dd></div>
                  <div><dt>Goals</dt><dd>{escape(persona["goals"])}</dd></div>
                  <div><dt>Skills</dt><dd>{escape(persona["skills"])}</dd></div>
                  <div><dt>Pain points</dt><dd>{escape(persona["pain_points"])}</dd></div>
                </dl>
              </div>
            </article>
            """
        )

    team_rows = [
        [escape(member["full_name"]), escape(member["student_number"]), escape(member["role_label"])]
        for member in team_members
    ]

    usage_list = "".join(f"<li>{escape(item)}</li>" for item in MISSION_COPY["how_to_use"])

    body = (
        section(
            "Why this atlas exists",
            f"<p>{escape(MISSION_COPY['statement'])}</p>"
            f'<div class="split-copy"><div><h3>How to use the site</h3><ol class="guide-list">{usage_list}</ol></div>'
            '<div><h3>Scope</h3><p>The app covers the landing, mission, shallow-glance, and deep-dive tasks described in the project brief, all from one SQLite-backed codebase.</p></div></div>',
            kicker="Mission",
        )
        + section("Target personas", "".join(persona_markup), kicker="Stored in SQLite", tone="contrast")
        + section(
            "Team members",
            data_table(
                ["Name", "Student number", "Role"],
                team_rows,
                "Team members pulled from the TeamMember table",
                "No team members are stored in the database yet.",
            ) + '<p class="footnote">Update the TeamMember table in app.db to replace the seeded placeholders with your real project members.</p>',
            kicker="Database-backed records",
        )
    )
    return page_template("Mission", "/mission", body, intro="Mission statement, personas, and team records are served directly from SQLite.")


def handle_vaccination_rates(config: AppConfig, query: dict[str, list[str]]) -> str:
    messages: list[str] = []
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        lookups = fetch_lookups(conn)
        antigen_values = {item["value"] for item in lookups["antigens"]}
        year_values = {item["value"] for item in lookups["years"]}
        region_values = {item["value"] for item in lookups["regions"]}
        country_values = {item["value"] for item in lookups["countries"]}

        antigen = validate_required_choice(first_value(query, "antigen"), antigen_values, "MCV1", "Antigen", messages)
        year = validate_required_choice(first_value(query, "year"), year_values, "2024", "Year", messages)
        region = validate_optional_choice(first_value(query, "region"), region_values, "Region", messages)
        country = validate_optional_choice(first_value(query, "country"), country_values, "Country", messages)
        sort_key = validate_required_choice(first_value(query, "sort"), set(VACCINATION_RATE_SORTS), "coverage_desc", "Sort order", messages)

        data = fetch_vaccination_rates(conn, antigen, int(year), region, country, sort_key)

    sort_options = [
        {"value": "coverage_desc", "label": "Coverage, high to low"},
        {"value": "coverage_asc", "label": "Coverage, low to high"},
        {"value": "country_asc", "label": "Country, A to Z"},
        {"value": "country_desc", "label": "Country, Z to A"},
        {"value": "region_asc", "label": "Region, A to Z"},
        {"value": "region_desc", "label": "Region, Z to A"},
    ]
    form = filter_form(
        "/vaccination-rates",
        [
            select_field("Antigen", "antigen", lookups["antigens"], antigen),
            select_field("Year", "year", lookups["years"], year),
            select_field("Region", "region", lookups["regions"], region, blank_label="All regions"),
            select_field("Country", "country", lookups["countries"], country, blank_label="All countries"),
            sort_field("Sort countries by", "sort", sort_options, sort_key),
        ],
    )

    country_rows = [
        [
            escape(row["antigen"]),
            escape(str(row["year"])),
            escape(row["country_name"]),
            escape(row["region_name"]),
            escape(f"{row['coverage_pct']:.2f}%"),
        ]
        for row in data["country_rows"]
    ]
    region_rows = [
        [
            escape(row["region_name"]),
            escape(str(row["countries_meeting_target"])),
        ]
        for row in data["region_rows"]
    ]
    chart = vertical_bar_chart(
        [(row["region_name"], float(row["countries_meeting_target"])) for row in data["region_rows"]],
        "Countries meeting the 90 percent threshold by region",
    )
    note = (
        f"<p class=\"footnote\">Rows with blank coverage values are excluded. "
        f"{data['excluded_count']} matching vaccination rows were omitted from the country table because coverage was not recorded.</p>"
    )
    if country:
        note += '<p class="footnote">The regional summary keeps the region comparison intact and does not narrow to a single country.</p>'

    body = (
        message_html(messages)
        + section(
            "Vaccination rates by country and region",
            f"<p>Use the filters to find countries with recorded coverage at or above 90 percent for the selected antigen and year.</p>{form}",
            kicker="Level 2A",
        )
        + section(
            "Countries meeting the target",
            data_table(
                ["Antigen", "Year", "Country", "Region", "Coverage"],
                country_rows,
                "Countries with recorded coverage at or above 90 percent",
                "No countries met the threshold for the current filters.",
            ) + note,
        )
        + section(
            "Regional summary",
            data_table(
                ["Region", "Countries at or above 90 percent"],
                region_rows,
                "Regional count of qualifying countries",
                "No regional summary rows were available for the current filters.",
            )
            + chart,
            tone="contrast",
        )
    )
    return page_template("Vaccination rates", "/vaccination-rates", body, intro="Focused view of vaccination coverage by country and region.")


def handle_infection_by_economy(config: AppConfig, query: dict[str, list[str]]) -> str:
    messages: list[str] = []
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        lookups = fetch_lookups(conn)
        economy_values = {item["value"] for item in lookups["economies"]}
        infection_values = {item["value"] for item in lookups["infection_types"]}
        year_values = {item["value"] for item in lookups["years"]}

        economy = validate_required_choice(first_value(query, "economy"), economy_values, "1", "Economic status", messages)
        infection = validate_required_choice(first_value(query, "infection"), infection_values, "MEA", "Infection type", messages)
        year = validate_required_choice(first_value(query, "year"), year_values, "2024", "Year", messages)
        sort_key = validate_required_choice(first_value(query, "sort"), set(INFECTION_ECONOMY_SORTS), "cases_per_100k_desc", "Sort order", messages)

        data = fetch_infection_by_economy(conn, int(economy), infection, int(year), sort_key)

    sort_options = [
        {"value": "cases_per_100k_desc", "label": "Cases per 100k, high to low"},
        {"value": "cases_per_100k_asc", "label": "Cases per 100k, low to high"},
        {"value": "cases_desc", "label": "Raw cases, high to low"},
        {"value": "cases_asc", "label": "Raw cases, low to high"},
        {"value": "country_asc", "label": "Country, A to Z"},
        {"value": "country_desc", "label": "Country, Z to A"},
    ]
    form = filter_form(
        "/infection-by-economy",
        [
            select_field("Economic status", "economy", lookups["economies"], economy),
            select_field("Infection type", "infection", lookups["infection_types"], infection),
            select_field("Year", "year", lookups["years"], year),
            sort_field("Sort countries by", "sort", sort_options, sort_key),
        ],
    )

    country_rows = [
        [
            escape(row["infection_name"]),
            escape(row["country_name"]),
            escape(row["economic_phase"]),
            escape(str(row["year"])),
            escape(format_number(row["raw_cases"])),
            escape(f"{row['cases_per_100k']:.2f}"),
        ]
        for row in data["country_rows"]
    ]
    summary_rows = [
        [escape(row["economic_phase"]), escape(format_number(row["total_cases"]))]
        for row in data["summary_rows"]
    ]
    chart = vertical_bar_chart(
        [(row["economic_phase"], float(row["total_cases"])) for row in data["summary_rows"]],
        "Total reported cases by economic phase",
    )
    body = (
        message_html(messages)
        + section(
            "Infection data by economic status",
            f"<p>Compare the infection burden for one economic phase, then contrast it with totals across all economic phases for the same year and infection type.</p>{form}",
            kicker="Level 2B",
        )
        + section(
            "Country results",
            data_table(
                ["Infection", "Country", "Economic phase", "Year", "Cases", "Cases per 100k"],
                country_rows,
                "Countries inside the selected economic phase",
                "No country rows matched the current filters.",
            ),
        )
        + section(
            "Summary by economic phase",
            data_table(
                ["Economic phase", "Total cases"],
                summary_rows,
                "Total cases by economic phase for the selected infection and year",
                "No summary rows were available for the current filters.",
            )
            + chart,
            tone="contrast",
        )
    )
    return page_template("Infection by economic status", "/infection-by-economy", body, intro="Focused infection comparison across economic phases.")


def handle_vaccination_improvement(config: AppConfig, query: dict[str, list[str]]) -> str:
    messages: list[str] = []
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        lookups = fetch_lookups(conn)
        antigen_values = {item["value"] for item in lookups["antigens"]}
        year_values = {item["value"] for item in lookups["years"]}

        antigen = validate_required_choice(first_value(query, "antigen"), antigen_values, "MCV1", "Antigen", messages)
        start_year = validate_required_choice(first_value(query, "start_year"), year_values, "2000", "Start year", messages)
        end_year = validate_required_choice(first_value(query, "end_year"), year_values, "2024", "End year", messages)
        limit = validate_limit(first_value(query, "limit"), 10, messages)
        sort_key = validate_required_choice(first_value(query, "sort"), set(VACCINATION_IMPROVEMENT_SORTS), "increase_desc", "Sort order", messages)

        rows: list[dict[str, object]] = []
        if int(start_year) >= int(end_year):
            messages.append("The start year must be earlier than the end year.")
        else:
            rows = fetch_vaccination_improvement(conn, antigen, int(start_year), int(end_year), limit, sort_key)

    sort_options = [
        {"value": "increase_desc", "label": "Rate increase, high to low"},
        {"value": "increase_asc", "label": "Rate increase, low to high"},
        {"value": "country_asc", "label": "Country, A to Z"},
        {"value": "country_desc", "label": "Country, Z to A"},
    ]
    form = filter_form(
        "/vaccination-improvement",
        [
            select_field("Antigen", "antigen", lookups["antigens"], antigen),
            select_field("Start year", "start_year", lookups["years"], start_year),
            select_field("End year", "end_year", lookups["years"], end_year),
            number_field("Country limit", "limit", limit, 1, 50),
            sort_field("Sort countries by", "sort", sort_options, sort_key),
        ],
    )
    table_rows = [
        [
            escape(row["country_name"]),
            escape(f"{row['rate_increase']:.2f}%"),
            escape(str(row["start_year"])),
            escape(str(row["end_year"])),
        ]
        for row in rows
    ]
    chart = horizontal_bar_chart(
        [(row["country_name"], float(row["rate_increase"])) for row in rows],
        "Vaccination rate increase by country",
        "%",
    )
    note = '<p class="footnote">Rate improvement is calculated as doses divided by population, then compared between the selected years. Blank dose fields and missing population rows are excluded.</p>'
    body = (
        message_html(messages)
        + section(
            "Biggest improvement in vaccination rate",
            f"<p>Find the countries with the largest jump in population-based vaccination rate for one antigen across a selected period.</p>{form}",
            kicker="Level 3A",
        )
        + section(
            "Top country results",
            data_table(
                ["Country", "Vaccination rate increase", "Start year", "End year"],
                table_rows,
                "Countries ranked by vaccination rate increase",
                "No improvement rows were available for the current filters.",
            ) + note,
        )
        + section("Rate jump chart", chart, tone="contrast")
    )
    return page_template("Vaccination improvement", "/vaccination-improvement", body, intro="Deep-dive ranking of countries with the biggest vaccination rate increase.")


def handle_above_average_infection(config: AppConfig, query: dict[str, list[str]]) -> str:
    messages: list[str] = []
    with closing(connect(source_db=config.source_db, app_db=config.app_db)) as conn:
        lookups = fetch_lookups(conn)
        infection_values = {item["value"] for item in lookups["infection_types"]}
        year_values = {item["value"] for item in lookups["years"]}

        infection = validate_required_choice(first_value(query, "infection"), infection_values, "MEA", "Infection type", messages)
        year = validate_required_choice(first_value(query, "year"), year_values, "2024", "Year", messages)
        sort_key = validate_required_choice(first_value(query, "sort"), set(ABOVE_AVERAGE_SORTS), "rate_desc", "Sort order", messages)

        data = fetch_above_average_infection(conn, infection, int(year), sort_key)

    sort_options = [
        {"value": "rate_desc", "label": "Rate, high to low"},
        {"value": "rate_asc", "label": "Rate, low to high"},
        {"value": "country_asc", "label": "Country, A to Z"},
        {"value": "country_desc", "label": "Country, Z to A"},
    ]
    form = filter_form(
        "/above-average-infection",
        [
            select_field("Infection type", "infection", lookups["infection_types"], infection),
            select_field("Year", "year", lookups["years"], year),
            sort_field("Sort countries by", "sort", sort_options, sort_key),
        ],
    )
    table_rows = [
        [
            escape(row["country_name"]),
            escape(f"{row['cases_per_100k']:.2f}"),
            escape(f"{row['global_cases_per_100k']:.2f}"),
        ]
        for row in data["rows"]
    ]
    chart = threshold_chart(
        [(row["country_name"], float(row["cases_per_100k"])) for row in data["rows"][:12]],
        float(data["global_rate"]),
        "Countries above the global infection rate",
        "",
    )
    global_value = f"{float(data['global_rate']):.2f}"
    body = (
        message_html(messages)
        + section(
            "Countries above the global infection rate",
            f"<p>Compare each country's infection rate with the global rate calculated for the same infection type and year.</p>{form}",
            kicker="Level 3B",
        )
        + section(
            "Global rate",
            f'<div class="spotlight-metric"><span class="spotlight-label">Global infection rate</span><strong>{escape(global_value)}</strong><span class="spotlight-note">Cases per 100,000 people in {escape(year)}</span></div>',
        )
        + section(
            "Countries above the threshold",
            data_table(
                ["Country", "Cases per 100k", "Global rate per 100k"],
                table_rows,
                "Countries whose rate exceeds the global rate",
                "No countries exceeded the global rate for the current filters.",
            ) + chart,
            tone="contrast",
        )
    )
    return page_template("Above-average infection", "/above-average-infection", body, intro="Find countries whose infection rate exceeds the global benchmark.")
