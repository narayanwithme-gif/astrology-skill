#!/usr/bin/env python3
"""Deterministic Jyotisha interpretive indicators from a local chart.json."""

import argparse
import json
from pathlib import Path

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGN_LORDS = [
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
]
HOUSE_TOPICS = {
    1: "self-direction, identity, and approach",
    2: "speech, learning, family resources, and values",
    3: "initiative, communication, practice, and siblings",
    4: "home, foundations, education, and inner steadiness",
    5: "creative work, study, discernment, and personal projects",
    6: "service, routines, competition, and problem-solving",
    7: "agreements, partnership, clients, and one-to-one work",
    8: "shared responsibilities, change, research, and uncertainty",
    9: "teachers, ethics, higher learning, and long journeys",
    10: "work, responsibility, contribution, and public role",
    11: "communities, long-range aims, collaboration, and gains",
    12: "retreat, rest, closure, expenses, and distant settings",
}
PLANET_THEMES = {
    "Sun": "purpose, visibility, leadership, and responsibility",
    "Moon": "attention, habits, care, and emotional responses",
    "Mars": "initiative, effort, courage, and conflict management",
    "Mercury": "learning, analysis, trade, and communication",
    "Jupiter": "teaching, judgment, counsel, and growth",
    "Venus": "art, enjoyment, relationships, and negotiation",
    "Saturn": "structure, persistence, limits, and long-term work",
    "Rahu": "ambition, experimentation, and unfamiliar approaches",
    "Ketu": "specialization, simplification, and detachment",
}


def rule_catalog():
    """Return 108 graha-in-bhava and 144 bhava-lord placement rule templates."""
    graha_rules = [
        {
            "id": f"graha-bhava-{planet.lower()}-{house:02d}",
            "type": "graha_in_bhava",
            "planet": planet,
            "bhava": house,
            "planet_themes": PLANET_THEMES[planet],
            "bhava_topics": HOUSE_TOPICS[house],
            "source_basis": "BPHS, chapters on bhava indications and graha-bhava phala",
        }
        for planet in PLANETS
        for house in range(1, 13)
    ]
    lord_rules = [
        {
            "id": f"bhava-lord-{ruled:02d}-in-{placed:02d}",
            "type": "bhava_lord_in_bhava",
            "ruled_bhava": ruled,
            "placed_bhava": placed,
            "source_basis": "BPHS, chapter 24: effects of bhava lords in the twelve houses",
        }
        for ruled in range(1, 13)
        for placed in range(1, 13)
    ]
    return {
        "count": len(graha_rules) + len(lord_rules),
        "graha_bhava_rules": graha_rules,
        "bhava_lord_rules": lord_rules,
        "note": "Templates are traditional interpretive prompts, not guaranteed events or scientific predictions.",
    }


def interpret_chart(jyotisha):
    """Build chart-specific graha/bhava and bhava-lord evidence cards."""
    planets = jyotisha["planets"]
    graha_cards = []
    for planet in PLANETS:
        if planet not in planets:
            continue
        house = int(planets[planet]["house"])
        if not 1 <= house <= 12:
            raise ValueError(f"Invalid whole-sign house for {planet}: {house}")
        graha_cards.append(
            {
                "rule_id": f"graha-bhava-{planet.lower()}-{house:02d}",
                "evidence": f"{planet} occupies bhava {house} ({planets[planet]['sign']}).",
                "themes": f"{PLANET_THEMES[planet]} in areas of {HOUSE_TOPICS[house]}.",
                "reading_prompt": "Check dignity, lordship, aspects, conjunctions, and relevant dasha before drawing a conclusion.",
            }
        )

    asc_sign = int(jyotisha["ascendant"]["sign_index"])
    lord_cards = []
    for ruled_house in range(1, 13):
        sign_index = (asc_sign + ruled_house - 1) % 12
        lord = SIGN_LORDS[sign_index]
        if lord not in planets:
            continue
        placed_house = int(planets[lord]["house"])
        lord_cards.append(
            {
                "rule_id": f"bhava-lord-{ruled_house:02d}-in-{placed_house:02d}",
                "evidence": f"The lord of bhava {ruled_house} is {lord}, placed in bhava {placed_house}.",
                "themes": f"{HOUSE_TOPICS[ruled_house]} connect with {HOUSE_TOPICS[placed_house]}.",
                "reading_prompt": "Qualify through the lord's dignity, aspects, conjunctions, divisional context, and dasha; this placement alone is not an outcome.",
            }
        )
    return {
        "source": "Brihat Parashara Hora Shastra, chapters 11–24 (house indications and bhava-lord placements)",
        "rule_library_size": 252,
        "graha_in_bhava": graha_cards,
        "bhava_lord_in_bhava": lord_cards,
        "count_for_chart": len(graha_cards) + len(lord_cards),
        "scope_note": "Traditional symbolic themes for reflection; no deterministic event, health, wealth, marriage, or lifespan forecasts.",
    }


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chart", required=True, help="chart.json from chart_engine.py")
    parser.add_argument("--out", required=True, help="output JSON file")
    parser.add_argument("--catalog", action="store_true", help="include all 252 rule templates")
    args = parser.parse_args()
    chart = json.loads(Path(args.chart).read_text(encoding="utf-8"))
    result = interpret_chart(chart["jyotisha"])
    if args.catalog:
        result["catalog"] = rule_catalog()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
