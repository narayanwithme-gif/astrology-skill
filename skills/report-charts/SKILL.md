---
name: report-charts
description: Design and render report charts, percentage bars, scorecards, and exact-value tables. Use for astrology reports, compatibility breakdowns, distributions, comparisons, and print-ready visuals from local data.
---

# Report charts

1. Identify the question and use the calculated JSON or supplied data as the source. Record the measure, unit, population, and applicable convention.
2. Use a horizontal bar for category comparisons. Use a line chart for genuine time-series data, with a date and measurement for each point. Use a table for lookups, degrees, settings, or exact dates. See [Report visuals](../../references/report-visuals.md) for the local renderer and examples.
3. For a percentage bar, supply the raw value and its denominator. Keep the scale at 0–100% and show the ratio and percentage beside the bar. For a share of a total, use the same total in every row. For scores with different maxima, identify the individual base and retain the raw score.
4. In astrology, normalize only a scored or counted quantity. Label a Guna Milan bar as points earned out of the method's maximum. Label a house distribution as the share of plotted bodies. Keep traditional statuses as text and preserve unknown or unavailable entries.
5. Use compact headings, direct labels, right-aligned numbers, and a restrained palette. Check that the chart and table agree and that labels remain readable on narrow screens and in A4 print preview.

Render HTML with `python scripts/report_visuals.py --spec visuals.json --out visuals.html` from the repository root, or use the installed `hermes-report-visuals` command.
