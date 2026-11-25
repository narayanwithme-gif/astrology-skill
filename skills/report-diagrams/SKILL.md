---
name: report-diagrams
description: Design readable timelines, process diagrams, and astrology chart layouts. Use for dasha periods, chart workflow, decision paths, and diagrams in offline reports.
---

# Report diagrams

1. Select one relationship to show. Use a timeline for dated intervals, an ordered step diagram for a workflow, a Mermaid flowchart for a decision with branches, and a table for an exact mapping.
2. For chart geometry, reuse the chart engine's Western wheel and North/South Indian charts. Preserve the zodiac, house method, divisional name, and ayanamsha in the caption. Use the chart JSON as the source for placements.
3. For a dasha timeline, use the calculated boundaries and label the timezone. Use proportional spacing for elapsed time. Provide exact dates as text and retain available uncertainty notes.
4. Give each node a short label. Label the condition on each branch, give the diagram one reading direction, and split large flows at changes of purpose. Keep essential information visible in text.
5. For an offline HTML deliverable, use the local renderer's timeline and steps sections. For branching in supporting Markdown, use Mermaid where the viewer supports it and include a short text equivalent. See [Report visuals](../../references/report-visuals.md) for examples and rendering commands.
