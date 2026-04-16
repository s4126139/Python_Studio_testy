from __future__ import annotations

import base64
from html import escape
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt


NAV_ITEMS = [
    ("/", "Overview"),
    ("/mission", "Mission"),
    ("/vaccination-rates", "Vaccination rates"),
    ("/infection-by-economy", "Economic status"),
    ("/vaccination-improvement", "Improvement"),
    ("/above-average-infection", "Above-average infection"),
]


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "N/A"
    if decimals == 0:
        return f"{int(round(float(value))):,}"
    return f"{float(value):,.{decimals}f}"


def format_compact(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    number = float(value)
    abs_number = abs(number)
    if abs_number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    if abs_number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if abs_number >= 1_000:
        return f"{number / 1_000:.2f}K"
    return format_number(number, 0)


def initials(label: str) -> str:
    parts = [part[0] for part in label.split() if part]
    return "".join(parts[:2]).upper() or "ID"


def nav_html(current_path: str) -> str:
    links = []
    for path, label in NAV_ITEMS:
        css_class = "nav-link active" if path == current_path else "nav-link"
        links.append(f'<a class="{css_class}" href="{path}">{escape(label)}</a>')
    return "".join(links)


def message_html(messages: list[str]) -> str:
    if not messages:
        return ""
    items = "".join(f"<li>{escape(message)}</li>" for message in messages)
    return f'<aside class="message-strip"><ul>{items}</ul></aside>'


def page_template(title: str, current_path: str, body: str, intro: str = "") -> str:
    intro_html = f'<p class="page-intro">{escape(intro)}</p>' if intro else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | Preventable Infectious Diseases Atlas</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a class="brand" href="/">PID Atlas</a>
      <nav class="site-nav" aria-label="Primary">{nav_html(current_path)}</nav>
    </div>
  </header>
  <main>
    {intro_html}
    {body}
  </main>
</body>
</html>"""


def overview_template(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Preventable Infectious Diseases Atlas</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body class="home-page">
  <header class="site-header site-header-home">
    <div class="site-header-inner">
      <a class="brand" href="/">PID Atlas</a>
      <nav class="site-nav" aria-label="Primary">{nav_html("/")}</nav>
    </div>
  </header>
  <main>{body}</main>
</body>
</html>"""


def section(title: str, body: str, kicker: str = "", tone: str = "") -> str:
    kicker_html = f'<p class="section-kicker">{escape(kicker)}</p>' if kicker else ""
    tone_class = f" section-{tone}" if tone else ""
    return f"""
    <section class="content-section{tone_class}">
      {kicker_html}
      <h2>{escape(title)}</h2>
      {body}
    </section>
    """


def select_field(label: str, name: str, options: list[dict[str, str]], selected: str, blank_label: str | None = None) -> str:
    option_html: list[str] = []
    if blank_label is not None:
        selected_attr = ' selected="selected"' if selected == "" else ""
        option_html.append(f'<option value=""{selected_attr}>{escape(blank_label)}</option>')
    for option in options:
        value = option["value"]
        selected_attr = ' selected="selected"' if value == selected else ""
        option_html.append(f'<option value="{escape(value)}"{selected_attr}>{escape(option["label"])}</option>')
    return f"""
    <label class="field">
      <span>{escape(label)}</span>
      <select name="{escape(name)}">
        {''.join(option_html)}
      </select>
    </label>
    """


def number_field(label: str, name: str, value: int, min_value: int, max_value: int, step: int = 1) -> str:
    return f"""
    <label class="field">
      <span>{escape(label)}</span>
      <input type="number" name="{escape(name)}" value="{value}" min="{min_value}" max="{max_value}" step="{step}">
    </label>
    """


def sort_field(label: str, name: str, options: list[dict[str, str]], selected: str) -> str:
    return select_field(label, name, options, selected)


def filter_form(action: str, fields: list[str], button_label: str = "Update view") -> str:
    return f"""
    <form class="filter-form" action="{escape(action)}" method="get">
      {''.join(fields)}
      <div class="field submit-field">
        <span>Apply</span>
        <button type="submit">{escape(button_label)}</button>
      </div>
    </form>
    """


def data_table(headers: list[str], rows: list[list[str]], caption: str, empty_message: str) -> str:
    if not rows:
        return f'<div class="empty-state"><p>{escape(empty_message)}</p></div>'
    thead = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"""
    <div class="table-wrap">
      <table>
        <caption>{escape(caption)}</caption>
        <thead><tr>{thead}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
      </table>
    </div>
    """


def fact_block(label: str, value: str, note: str) -> str:
    return f"""
    <div class="fact">
      <p class="fact-label">{escape(label)}</p>
      <p class="fact-value">{escape(value)}</p>
      <p class="fact-note">{escape(note)}</p>
    </div>
    """


def stat_band(items: list[str]) -> str:
    return f'<section class="fact-band">{"".join(items)}</section>'


def route_link(label: str, href: str, summary: str) -> str:
    return f"""
    <a class="route-link" href="{escape(href)}">
      <span class="route-link-label">{escape(label)}</span>
      <span class="route-link-summary">{escape(summary)}</span>
    </a>
    """


def chart_shell(title: str, subtitle: str, image_markup: str) -> str:
    return f"""
    <figure class="chart-frame">
      <figcaption>
        <strong>{escape(title)}</strong>
        <span>{escape(subtitle)}</span>
      </figcaption>
      {image_markup}
    </figure>
    """


def wrap_label(label: str, width: int = 14) -> str:
    words = label.split()
    if len(label) <= width or len(words) < 2:
        return label
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        proposal = f"{current} {word}"
        if len(proposal) <= width:
            current = proposal
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return "\n".join(lines[:3])


def render_plot_image(fig: plt.Figure, alt_text: str) -> str:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f'<img class="chart-image" src="data:image/png;base64,{encoded}" alt="{escape(alt_text)}">'


def base_axes_style(ax: plt.Axes) -> None:
    ax.set_facecolor("#fffdf9")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#b8b1a6")
    ax.spines["bottom"].set_color("#b8b1a6")
    ax.tick_params(colors="#34403b")
    ax.grid(axis="y", color="#e8dfd1", linewidth=0.8)
    ax.set_axisbelow(True)


def vertical_bar_chart(items: list[tuple[str, float]], title: str) -> str:
    if not items:
        return chart_shell(title, "No rows matched the current filters.", '<div class="empty-state"><p>No chart data available.</p></div>')

    labels = [wrap_label(label) for label, _ in items]
    values = [value for _, value in items]
    fig, ax = plt.subplots(figsize=(8.2, 3.8), constrained_layout=True)
    fig.patch.set_facecolor("#fffdf9")
    base_axes_style(ax)
    bars = ax.bar(labels, values, color="#0d6a68", width=0.62)
    ax.set_title(title, fontsize=12, loc="left", color="#16211d")
    ax.tick_params(axis="x", labelrotation=0, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            format_compact(value),
            ha="center",
            va="bottom",
            fontsize=8,
            color="#16211d",
        )

    image = render_plot_image(fig, title)
    return chart_shell(title, "Matplotlib image generated on the server.", image)


def horizontal_bar_chart(items: list[tuple[str, float]], title: str, unit_suffix: str) -> str:
    if not items:
        return chart_shell(title, "No rows matched the current filters.", '<div class="empty-state"><p>No chart data available.</p></div>')

    labels = [label for label, _ in items][::-1]
    values = [value for _, value in items][::-1]
    fig_height = max(3.2, 0.46 * len(items) + 1.2)
    fig, ax = plt.subplots(figsize=(8.4, fig_height), constrained_layout=True)
    fig.patch.set_facecolor("#fffdf9")
    base_axes_style(ax)
    bars = ax.barh(labels, values, color="#0d6a68", height=0.58)
    ax.set_title(title, fontsize=12, loc="left", color="#16211d")
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"  {value:.2f}{unit_suffix}",
            va="center",
            ha="left",
            fontsize=8,
            color="#16211d",
        )

    image = render_plot_image(fig, title)
    return chart_shell(title, "Largest values are shown with the longest bars.", image)


def threshold_chart(items: list[tuple[str, float]], threshold: float, title: str, unit_suffix: str) -> str:
    if not items:
        return chart_shell(title, "No rows matched the current filters.", '<div class="empty-state"><p>No chart data available.</p></div>')

    labels = [label for label, _ in items][::-1]
    values = [value for _, value in items][::-1]
    fig_height = max(3.2, 0.46 * len(items) + 1.2)
    fig, ax = plt.subplots(figsize=(8.4, fig_height), constrained_layout=True)
    fig.patch.set_facecolor("#fffdf9")
    base_axes_style(ax)
    bars = ax.barh(labels, values, color="#0d6a68", height=0.58)
    ax.axvline(threshold, color="#b8662f", linestyle="--", linewidth=1.6, label=f"Global rate {threshold:.2f}{unit_suffix}")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    ax.set_title(title, fontsize=12, loc="left", color="#16211d")
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"  {value:.2f}{unit_suffix}",
            va="center",
            ha="left",
            fontsize=8,
            color="#16211d",
        )

    image = render_plot_image(fig, title)
    return chart_shell(title, "The reference line marks the global rate used as the threshold.", image)
