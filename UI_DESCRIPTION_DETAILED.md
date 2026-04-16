# PID Atlas UI Specification

## 1. Purpose of This Document

This document is written as an implementation-ready UI specification for the project **Preventable Infectious Diseases Atlas (PID Atlas)**.

It is intended to be detailed enough for:

- a human designer or developer who has never seen the project before
- an AI coding or design system that needs to reconstruct the interface

The document explains:

- what the project is
- who the product is for
- what screens exist
- how the screens are organized
- what content, controls, and data each screen must contain
- how the interface should look and behave
- what states and edge cases must be handled

The target outcome is a complete, faithful recreation of the current UI, not a generic dashboard replacement.

## 2. Product Identity

Full project name:

- **Preventable Infectious Diseases Atlas**

Short brand name used in the interface:

- **PID Atlas**

Product type:

- public data website
- read-only analytical interface
- server-rendered web application
- no login
- no account system
- no record editing from the UI

Core product goal:

- transform the provided immunisation dataset into a structured public-facing atlas
- help users understand vaccination coverage, disease burden, regional differences, economic differences, and country-level outliers
- communicate evidence clearly without hiding missing data or overstating conclusions

## 3. Technical Context That Shapes the UI

The current system is implemented as:

- Python WSGI application
- SQLite-backed data layer
- server-rendered HTML
- one shared CSS stylesheet
- Matplotlib-generated chart images rendered on the server

This affects the UI in important ways:

- pages are document-like rather than app-like
- filters submit with `GET`
- page state is visible in the query string
- full-page reloads are normal behavior
- charts are static images, not interactive JavaScript charts

Any rebuilt UI should preserve this calm, report-style interaction model unless the project is intentionally being redesigned.

## 4. Intended Users

The UI is designed for three main user types that are already represented in the project data.

### 4.1. Public Health Researcher

Example persona: **Dr Maya Chen**

Needs:

- trustworthy rates
- region comparison
- explicit caveats about missing records

### 4.2. Policy Adviser

Example persona: **Nadia Rahman**

Needs:

- concise summaries
- sortable country tables
- defensible wording for briefing use

### 4.3. Medical Student or Guided Learner

Example persona: **Elias Morgan**

Needs:

- plain-language framing
- gradual entry into the data
- guidance before deeper analysis

The UI therefore needs to be:

- structured
- readable
- calm
- evidence-led
- explicit about what each page is doing

## 5. Data Scope Exposed Through the UI

The current UI is grounded in real values from the existing database.

### 5.1. Headline Scope

- Time span: **2000-2024**
- Countries: **217**
- Regions: **7**
- Economic groups: **4**
- Antigens in filter controls: **5**
- Infection types in filter controls: **3**

### 5.2. Homepage Summary Metrics

- Dataset span: **2000-2024**
- Countries: **217**
- Recorded numeric doses: **10.62B**
- Reported infection cases: **19.23M**

### 5.3. Antigen Lookup Values

- `DTPCV1` - DTP-containing vaccine, 1st dose
- `DTPCV3` - DTP-containing vaccine, 3rd dose
- `MCV1` - Measles-containing vaccine, 1st dose
- `MCV2` - Measles-containing vaccine, 2nd dose
- `RCV1` - Rubella-containing vaccine, 1st dose

### 5.4. Infection Type Lookup Values

- `MEA` - Measles
- `PER` - Pertussis
- `RUB` - Rubella

### 5.5. Economic Phase Lookup Values

- `1` - High Income
- `2` - Upper Middle Income
- `3` - Lower Middle Income
- `4` - Low Income

### 5.6. Region Lookup Values

- `TEA` - East Asia & Pacific
- `TEC` - Europe & Central Asia
- `TLA` - Latin America & Carribean
- `TMN` - Middle East, North Africa, Afghanistan & Pakistan
- `NAC` - North America
- `TSA` - South Asia
- `TSS` - Sub-Saharan Africa

## 6. Information Architecture

The product currently has six top-level routes:

1. `/` - Overview
2. `/mission` - Mission
3. `/vaccination-rates` - Vaccination rates
4. `/infection-by-economy` - Economic status
5. `/vaccination-improvement` - Improvement
6. `/above-average-infection` - Above-average infection

### 6.1. Header Navigation Labels

The navigation order must be:

1. Overview
2. Mission
3. Vaccination rates
4. Economic status
5. Improvement
6. Above-average infection

### 6.2. User Flow Logic

The intended progression is:

1. user lands on Overview
2. user understands the product and available routes
3. user chooses a focused analytical page
4. user filters, sorts, and reads tabular output
5. user uses charts and benchmark sections to interpret the results

## 7. Global Visual Style

The design should feel like a modern analytical report rather than a generic admin dashboard.

Key qualities:

- credible
- warm
- calm
- editorial
- readable
- structured

Avoid:

- neon or saturated UI accents
- excessive cards and widgets
- playful or cartoon-like styling
- over-animated interactions
- dense dashboard clutter

## 8. Core Design Tokens

These values come from the implemented CSS and should be treated as the primary design system.

### 8.1. Color Tokens

- `--paper`: `#f5efe5`
- `--panel`: `#fbf7f0`
- `--ink`: `#16211d`
- `--muted`: `#56635e`
- `--line`: `rgba(22, 33, 29, 0.14)`
- `--accent`: `#0d6a68`
- `--accent-strong`: `#084948`
- `--accent-soft`: `#d7ece7`
- `--signal`: `#b8662f`
- `--shadow`: `0 18px 40px rgba(15, 32, 28, 0.08)`

### 8.2. Typography Tokens

- Display font: `"Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif`
- UI font: `"Trebuchet MS", Verdana, sans-serif`

### 8.3. Background Treatment

The body background is layered, not flat:

- a soft radial teal tint near the top-left
- a paper-like vertical gradient from light cream to deeper beige

This should be preserved because it gives the site character while keeping it highly readable.

### 8.4. Motion

- enter animation: `rise-in`
- duration: `720ms`
- easing: `ease`
- direction: upward fade-in

## 9. Layout Rules

### 9.1. Width Constraints

- header width: `min(1180px, calc(100vw - 2rem))`
- content width: `min(1120px, calc(100vw - 2rem))`

### 9.2. Global Layout Principles

- content should feel centered and stable
- line length should remain readable
- sections should be visually separated
- tables should keep their tabular structure instead of collapsing into unrelated card patterns

### 9.3. Primary Layout Patterns

- two-column hero on desktop
- one-column stacking on narrower screens
- route-link grid
- filter-form grid
- panel-based section layout

## 10. Shared UI Components

The project uses a consistent set of reusable patterns. A rebuild should keep them.

### 10.1. Sticky Header

Must include:

- brand link on the left
- primary nav on the right
- active route highlighting

Variants:

- homepage header
- inner-page header

### 10.2. Page Intro

Used on non-home pages.

Purpose:

- provide a short summary line below the header and before the first section

### 10.3. Content Section Panel

Purpose:

- group content into readable analytical blocks

Required traits:

- border
- soft background
- internal padding
- box shadow
- heading hierarchy

Variant:

- default light panel
- dark contrast panel

### 10.4. Section Kicker

Purpose:

- mark the page level, content type, or section grouping

Examples:

- Mission
- Stored in SQLite
- Database-backed records
- Level 2A
- Level 2B
- Level 3A
- Level 3B

### 10.5. Filter Form

Must support:

- labeled form fields
- select controls
- number input when required
- a final submit action

Presentation rules:

- uppercase micro-label above each field
- rounded controls
- full-width controls within each field cell
- a final submit block with the micro-label `Apply`
- default submit button label `Update view`

### 10.6. Data Table

Must include:

- caption
- header row
- scrollable wrapper on narrow screens
- consistent alignment

### 10.7. Chart Frame

Must include:

- chart title
- chart subtitle
- chart content or empty state

Current subtitle behavior in the implemented UI:

- vertical bar charts use `Matplotlib image generated on the server.`
- horizontal bar charts use `Largest values are shown with the longest bars.`
- threshold charts use `The reference line marks the global rate used as the threshold.`
- empty chart states use `No rows matched the current filters.`

### 10.8. Fact Block

Used only on the homepage.

Must include:

- small label
- large value
- brief note

### 10.9. Route Link Card

Used only on the homepage.

Must include:

- route label
- route summary

Interaction:

- subtle hover lift
- stronger border emphasis on hover

### 10.10. Persona Panel

Used on the Mission page.

Must include:

- circular initials avatar
- name
- headline
- structured details for:
  - Demographic
  - Needs
  - Goals
  - Skills
  - Pain points

### 10.11. Spotlight Metric

Used on the Above-average infection page.

Must include:

- small label
- very large metric value
- note describing the unit and selected year

### 10.12. Message Strip

Purpose:

- show validation messages and parameter fallback notes

### 10.13. Empty State

Purpose:

- explain clearly when no rows match the active filters

## 11. Responsive Behavior

The design must remain usable on desktop, tablet, and mobile.

### 11.1. Breakpoint Around 980px

At this width:

- the hero becomes one column
- the route grid becomes one column
- split-copy layouts become one column
- the fact band becomes two columns
- the persona detail grid becomes one column

### 11.2. Breakpoint Around 720px

At this width:

- the header stacks vertically
- navigation moves below the brand
- the hero becomes less height-driven
- the fact band becomes one column
- persona panels become vertical
- the persona avatar becomes smaller

### 11.3. Mobile Priorities

On mobile, preserve:

- readable text blocks
- usable filter controls
- accessible navigation
- scrollable tables when needed

## 12. Accessibility and Readability Requirements

The UI should behave like a responsible public data interface.

Requirements:

- clear heading hierarchy
- visible active route
- visible hover and focus states
- readable color contrast
- descriptive table captions
- descriptive chart alt text
- no key information conveyed only through color

Charts should always be understandable through:

- chart title
- subtitle
- nearby table or explanatory copy
- threshold lines where applicable

## 13. Data Model Relevant to the UI

### 13.1. Reference Tables

`Country`

- `CountryID`
- `name`
- `region`
- `economy`

`Region`

- `RegionID`
- `region`

`Economy`

- `economyID`
- `phase`

`Antigen`

- `AntigenID`
- `name`

`Infection_Type`

- `id`
- `description`

`YearDate`

- `YearID`

### 13.2. Data Tables

`Vaccination`

- `inf_type`
- `antigen`
- `country`
- `year`
- `target_num`
- `doses`
- `coverage`

`CountryPopulation`

- `country`
- `year`
- `population`

`InfectionData`

- `inf_type`
- `country`
- `year`
- `cases`

### 13.3. App-Specific Content Tables

`Persona`

- `slug`
- `name`
- `headline`
- `demographic`
- `needs`
- `goals`
- `skills`
- `pain_points`
- `image_path`
- `display_order`

`TeamMember`

- `full_name`
- `student_number`
- `role_label`
- `display_order`

## 14. Route-by-Route UI Contract

Each route below defines what a reconstructed UI must contain.

## 14.1. Overview Page

URL:

- `/`

Purpose:

- introduce the product
- establish trust through real metrics
- guide the user into deeper analysis

Header behavior:

- homepage header variant

### Hero Section

Kicker:

- `Global immunisation evidence, rendered from the provided SQLite dataset.`

Title:

- `Preventable Infectious Diseases Atlas`

Body copy:

- `A server-rendered reference for reading vaccination progress, infection burden, and outlier countries without leaving the underlying data context behind.`

Primary action:

- `Start with rates` -> `/vaccination-rates`

Secondary action:

- `Read the mission` -> `/mission`

Layout:

- left column for copy and actions
- right column for the overview chart

### Overview Chart

Type:

- vertical bar chart

Title:

- `Total reported cases by infection type`

Data categories:

- Measles
- Pertussis
- Rubella

### Fact Band

Must contain four fact blocks:

1. `Dataset span`
2. `Countries`
3. `Recorded numeric doses`
4. `Reported infection cases`

Each fact block must include:

- label
- large value
- supporting note

### Route Grid

Heading kicker:

- `Six routes, one dataset`

Heading:

- `Choose the level of detail you need`

Supporting text:

- `Begin with the big picture, then move into filterable and ranked views that stay grounded in raw SQL and server-side Matplotlib output.`

Route cards:

1. `Mission and audience`
2. `Vaccination rates`
3. `Economic status view`
4. `Vaccination improvement`
5. `Above-average infection`

Current route-card summaries:

- `Mission and audience` -> `Purpose, usage, personas, and team records from the database.`
- `Vaccination rates` -> `Find countries and regions meeting 90 percent coverage.`
- `Economic status view` -> `Compare infection burden by economic phase.`
- `Vaccination improvement` -> `Measure the biggest rate jump across a chosen period.`
- `Above-average infection` -> `Surface countries whose infection rate exceeds the global rate.`

## 14.2. Mission Page

URL:

- `/mission`

Page intro:

- `Mission statement, personas, and team records are served directly from SQLite.`

Purpose:

- explain the product mission
- show intended audiences
- show team ownership

### Section A: Why This Atlas Exists

Kicker:

- `Mission`

Title:

- `Why this atlas exists`

Mission statement content:

- the atlas turns the provided WHO-style immunisation dataset into an explorable public reference
- the site keeps a neutral tone
- the site states where missing vaccination values limit interpretation

Split content block:

- left side heading: `How to use the site`
- right side heading: `Scope`

How-to-use list:

1. start on the overview page
2. use the middle pages for filtered comparison
3. use the deep-dive pages for outliers and change analysis

Scope text:

- the app covers landing, mission, shallow-glance, and deep-dive tasks from the project brief

### Section B: Target Personas

Kicker:

- `Stored in SQLite`

Title:

- `Target personas`

Tone:

- contrast section

Content requirements:

- one persona panel per persona record
- each panel includes initials avatar, name, headline, and the five required fields
- the current implementation uses initials only and does not render `image_path`

### Section C: Team Members

Kicker:

- `Database-backed records`

Title:

- `Team members`

Table columns:

- Name
- Student number
- Role

Caption:

- `Team members pulled from the TeamMember table`

Footnote:

- current placeholders should be replaced with real student members

## 14.3. Vaccination Rates Page

URL:

- `/vaccination-rates`

Page intro:

- `Focused view of vaccination coverage by country and region.`

Purpose:

- show countries that meet the 90 percent threshold
- summarize qualifying counts by region

Lead section title:

- `Vaccination rates by country and region`

Lead section kicker:

- `Level 2A`

Support text:

- `Use the filters to find countries with recorded coverage at or above 90 percent for the selected antigen and year.`

### Filters

Method:

- `GET`

Action:

- `/vaccination-rates`

Fields:

- `antigen`
- `year`
- `region`
- `country`
- `sort`

Blank options:

- region supports `All regions`
- country supports `All countries`

Default values:

- `antigen=MCV1`
- `year=2024`
- `region=` blank
- `country=` blank
- `sort=coverage_desc`

Sort labels:

- Coverage, high to low
- Coverage, low to high
- Country, A to Z
- Country, Z to A
- Region, A to Z
- Region, Z to A

### Output Section A

Title:

- `Countries meeting the target`

Caption:

- `Countries with recorded coverage at or above 90 percent`

Table columns:

- Antigen
- Year
- Country
- Region
- Coverage

Table logic:

- only include rows with numeric coverage of at least 90
- exclude rows with blank coverage

Required note:

- report how many rows were excluded due to missing coverage
- if a country filter is active, add a second note explaining that the regional summary remains comparative and does not narrow to a single country

Empty state:

- `No countries met the threshold for the current filters.`

### Output Section B

Title:

- `Regional summary`

Tone:

- contrast section

Caption:

- `Regional count of qualifying countries`

Table columns:

- Region
- Countries at or above 90 percent

Chart:

- vertical bar chart
- title: `Countries meeting the 90 percent threshold by region`

Empty state:

- `No regional summary rows were available for the current filters.`

Validation behavior:

- invalid required values fall back to defaults
- invalid optional filters are cleared
- feedback appears in the message strip

Common messages:

- `Antigen was not recognised, so the default value was used.`
- `Year was not recognised, so the default value was used.`
- `Region was not recognised, so that filter was cleared.`
- `Country was not recognised, so that filter was cleared.`
- `Sort order was not recognised, so the default value was used.`

## 14.4. Infection by Economic Status Page

URL:

- `/infection-by-economy`

Page intro:

- `Focused infection comparison across economic phases.`

Purpose:

- compare disease burden inside one economic group
- compare total cases across all economic phases

Lead section title:

- `Infection data by economic status`

Lead section kicker:

- `Level 2B`

Support text:

- `Compare the infection burden for one economic phase, then contrast it with totals across all economic phases for the same year and infection type.`

### Filters

Fields:

- `economy`
- `infection`
- `year`
- `sort`

Default values:

- `economy=1`
- `infection=MEA`
- `year=2024`
- `sort=cases_per_100k_desc`

Sort labels:

- Cases per 100k, high to low
- Cases per 100k, low to high
- Raw cases, high to low
- Raw cases, low to high
- Country, A to Z
- Country, Z to A

### Output Section A

Title:

- `Country results`

Caption:

- `Countries inside the selected economic phase`

Table columns:

- Infection
- Country
- Economic phase
- Year
- Cases
- Cases per 100k

Purpose of table:

- compare countries within the selected economic phase

Empty state:

- `No country rows matched the current filters.`

### Output Section B

Title:

- `Summary by economic phase`

Tone:

- contrast section

Caption:

- `Total cases by economic phase for the selected infection and year`

Table columns:

- Economic phase
- Total cases

Chart:

- vertical bar chart
- title: `Total reported cases by economic phase`

Empty state:

- `No summary rows were available for the current filters.`

Validation messages can include:

- `Economic status was not recognised, so the default value was used.`
- `Infection type was not recognised, so the default value was used.`
- `Year was not recognised, so the default value was used.`
- `Sort order was not recognised, so the default value was used.`

## 14.5. Vaccination Improvement Page

URL:

- `/vaccination-improvement`

Page intro:

- `Deep-dive ranking of countries with the biggest vaccination rate increase.`

Purpose:

- rank countries by how much vaccination rate increased between two years

Lead section title:

- `Biggest improvement in vaccination rate`

Lead section kicker:

- `Level 3A`

Support text:

- `Find the countries with the largest jump in population-based vaccination rate for one antigen across a selected period.`

### Filters

Fields:

- `antigen`
- `start_year`
- `end_year`
- `limit`
- `sort`

Default values:

- `antigen=MCV1`
- `start_year=2000`
- `end_year=2024`
- `limit=10`
- `sort=increase_desc`

Limit control:

- minimum `1`
- maximum `50`
- whole numbers only

Sort labels:

- Rate increase, high to low
- Rate increase, low to high
- Country, A to Z
- Country, Z to A

### Output Section A

Title:

- `Top country results`

Caption:

- `Countries ranked by vaccination rate increase`

Table columns:

- Country
- Vaccination rate increase
- Start year
- End year

Required explanatory note:

- improvement is calculated using doses divided by population
- blank doses and missing population rows are excluded

Empty state:

- `No improvement rows were available for the current filters.`

### Output Section B

Title:

- `Rate jump chart`

Tone:

- contrast section

Chart:

- horizontal bar chart
- title: `Vaccination rate increase by country`
- unit suffix: `%`

Validation messages can include:

- `Antigen was not recognised, so the default value was used.`
- `Start year was not recognised, so the default value was used.`
- `End year was not recognised, so the default value was used.`
- `Sort order was not recognised, so the default value was used.`
- `The country limit must be a whole number, so the default value was used.`
- `The country limit must stay between 1 and 50, so the default value was used.`
- `The start year must be earlier than the end year.`

## 14.6. Above-Average Infection Page

URL:

- `/above-average-infection`

Page intro:

- `Find countries whose infection rate exceeds the global benchmark.`

Purpose:

- calculate the global infection benchmark for the selected year and disease
- show countries above that benchmark

Lead section title:

- `Countries above the global infection rate`

Lead section kicker:

- `Level 3B`

Support text:

- `Compare each country's infection rate with the global rate calculated for the same infection type and year.`

### Filters

Fields:

- `infection`
- `year`
- `sort`

Default values:

- `infection=MEA`
- `year=2024`
- `sort=rate_desc`

Sort labels:

- Rate, high to low
- Rate, low to high
- Country, A to Z
- Country, Z to A

### Output Section A

Title:

- `Global rate`

Content type:

- spotlight metric

Required contents:

- label: `Global infection rate`
- large numeric value
- note: `Cases per 100,000 people in [year]`

### Output Section B

Title:

- `Countries above the threshold`

Tone:

- contrast section

Caption:

- `Countries whose rate exceeds the global rate`

Table columns:

- Country
- Cases per 100k
- Global rate per 100k

Chart:

- horizontal threshold chart
- title: `Countries above the global infection rate`
- chart input is limited to the first 12 sorted country rows in the current implementation
- includes a dashed benchmark line
- includes a legend describing the threshold

Empty state:

- `No countries exceeded the global rate for the current filters.`

Validation messages can include:

- `Infection type was not recognised, so the default value was used.`
- `Year was not recognised, so the default value was used.`
- `Sort order was not recognised, so the default value was used.`

## 15. Chart Rules

Charts are required outputs, not decoration.

Rules:

- every major analytical page must include a chart
- every chart must sit inside a framed figure
- every chart must include title and subtitle
- chart colors should match the site palette
- chart images must include alt text

Chart types in the current UI:

- vertical bar chart
- horizontal bar chart
- threshold chart with dashed benchmark line

If no chart data exists:

- keep the chart frame visible
- show a no-data message

## 16. Validation, Empty States, and Safe Fallbacks

The application should never fail hard because of invalid user filters.

Required behavior:

- invalid required filter values revert to a default
- invalid optional filters are cleared
- invalid numeric values revert to a safe default
- explanatory messages appear near the top of the page

Required empty-state behavior:

- tables show a human-readable message when no rows match
- charts show a no-data message when the chart dataset is empty
- page layout remains intact

This is important because the product should feel stable and trustworthy even when filters produce no result.

## 16.1. Secondary Error Outputs

These states are part of the current project output and should be documented if the goal is a faithful recreation.

### 404 Not Found

Behavior:

- uses the normal page template
- page title is `Page not found`
- the body contains a content section with:
  - heading: `Page not found`
  - paragraph: `The requested route does not exist.`

### 405 Method Not Allowed

Behavior:

- returned for any non-`GET` request
- does not use the normal page template
- current output is a minimal HTML response containing only `Method not allowed`

This 405 behavior is intentionally simpler than the rest of the UI and should not be mistaken for a styled page.

## 17. Rebuild Guidance for Humans and AI

If rebuilding the project, the safest order is:

1. build the global shell and header
2. build the reusable section, table, chart, and form components
3. build the Overview page
4. build the Mission page
5. build the three filter-driven analytical pages
6. build the two deep-dive analytical pages
7. connect all pages to the real query layer
8. add validation messages and empty states
9. verify responsive behavior

Non-negotiable features to preserve:

- the six-route structure
- sticky navigation
- server-style document layout
- page-specific filters
- table-plus-chart pairing on analytical pages
- persona section on Mission
- spotlight metric on Above-average infection
- visible handling of missing or invalid input

## 18. Acceptance Checklist for a Complete UI Recreation

A recreation of this UI should only be considered complete if all items below are true.

- the application contains six primary routes matching the current information architecture
- the sticky header is visible on all pages
- the active navigation item is visually highlighted
- the Overview page contains a hero, chart, fact band, and route grid
- the Mission page contains a mission section, personas section, and team section
- the Vaccination rates page exposes antigen, year, region, country, and sort controls
- the Vaccination rates page shows both a country table and a region summary table/chart
- the Infection by economic status page exposes economy, infection, year, and sort controls
- the Infection by economic status page shows both a country table and an economic-phase summary table/chart
- the Vaccination improvement page exposes antigen, start year, end year, limit, and sort controls
- the Vaccination improvement page validates the year range and limit field
- the Vaccination improvement page includes a ranked table and a horizontal bar chart
- the Above-average infection page exposes infection, year, and sort controls
- the Above-average infection page includes a spotlight metric for the global rate
- the Above-average infection page includes both a threshold table and a threshold chart
- every analytical page shows a clear empty state when no rows are available
- invalid query parameters produce inline feedback instead of a broken page
- the interface remains readable on tablet and mobile widths
- the visual tone still feels like an evidence-led atlas rather than an admin CRUD dashboard

## 19. Final Summary

PID Atlas is not simply a collection of charts and tables. It is a structured analytical interface with a deliberate flow:

- first explain the dataset
- then orient the user
- then provide filtered analytical pages
- then provide deeper ranked and benchmark-based views

To rebuild the project faithfully, an implementer must preserve both the visible design and the hidden logic behind it:

- the route structure
- the content hierarchy
- the exact filter groups
- the page-specific outputs
- the fallback behavior
- the editorial visual tone

If those pieces are preserved, a human or AI implementer should be able to recreate a complete UI that accurately represents the project.
