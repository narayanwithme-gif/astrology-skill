# Jyotisha indicators and ten Poruthams

## 252-rule interpretive library

`scripts/vedic_predictions.py` provides a local deterministic interpretation
layer over the chart engine's D1 whole-sign positions. It exposes 108 graha-in-
bhava combinations (9 grahas × 12 bhavas) and 144 bhava-lord-in-bhava
combinations (12 lords × 12 placements). A chart produces up to 21 applicable
cards: one for each of nine graha placements and one for each bhava lord.

The rule structure follows the house topics and placement-oriented chapters of
the *Brihat Parashara Hora Shastra* (BPHS), especially chapters 11–24. The cards
are evidence-linked themes and questions, not guaranteed events. The result
does not predict health diagnoses, lifespan, investment returns, spouse death,
or other deterministic outcomes. Strength, lordship, aspects, divisional context,
birth-time quality, and dasha must be weighed in an actual traditional reading.

Run the chart-specific JSON output with:

```sh
hermes-vedic-predictions --chart reports/demo/chart.json --out reports/demo/vedic-indicators.json
```

Add the entire 252-template catalog to that output with `--catalog`. The reading
generator includes the chart-specific indicators automatically. The count
describes the rule library, not the number of conclusions emitted for a chart.

Primary text reference: [BPHS, English translation, chapters 11–24](https://www.horasad.com/download/ebooks/BRIHAT_PARASHARA_HORA_SHASTRA_1.pdf).
The translator and classical text both warn that results must be judged through
the full chart rather than one placement in isolation.

## Tamil Dasa Porutham: ten checks

The compatibility extension adds the South Indian/Tamil ten checks alongside
existing Ashtakoota: Dina, Gana, Mahendra, Stree Deergha, Yoni, Rasi,
Rasyadhipathi, Vasya, Rajju, and Vedha. The primary source for this selected
convention is [Vidhānamālai, chapter 11, Kadimanam](https://jyotisha.vedicreader.com/s/shl?s=5a0f5c8bdf0&sec=%E0%AE%AA%E0%AE%BE%E0%AE%9F%E0%AE%B2%E0%AF%8D+32), with cross-checks against
[*Kalaprakasika*, chapter 13](https://www.astrojyoti.com/wp-content/uploads/2019/09/Kalaprakasika_text.pdf).

| Check | Implemented convention |
|---|---|
| Dina | Count from girl's birth star to boy's; counts 2/4/6/8/9 are favorable in the first nine, all but 17 in the second nine, and all but 24/27 in the third nine |
| Gana | Same gana favorable; girl's Manushya with boy's Deva favorable; girl's Deva with boy's Manushya partial; other differing pairs fail this implementation |
| Mahendra | Girl-to-boy counts 4, 7, 10, 13, 16, 19, 22, 25 are favorable |
| Stree Deergha | Girl-to-boy count greater than 13 is favorable |
| Yoni | The source's star-to-animal associations; same animal and monkey pairings are favorable, listed hostile-animal pairs unfavorable, other pairs partial |
| Rasi | Count from girl's Moon sign to boy's; same sign and 7–12 favorable, 2/5/6 unfavorable, 3/4 partial |
| Rasyadhipathi | Natural Moon-sign-lord relationship: mutual friends favorable, neutral or mixed partial, any enemy relation unfavorable |
| Vasya | Source's directional Moon-sign attraction table; girl's sign attracting the boy's is favorable, reverse-only attraction partial |
| Rajju | Same birth-star Rajju group is unfavorable |
| Vedha | The selected source's mutually obstructing star pairs, including the Mrigashira–Chitra–Dhanishta group |

Output reports ten raw checks and counts of favorable, partial, and unfavorable
results. It does not issue a marriage recommendation or apply cancellation
rules. Porutham tables, role conventions, thresholds, and exceptions vary
between regional almanacs; the method and its caveats are included in the JSON.
The traditional texts describe this as a symbolic compatibility practice, not
an empirical relationship assessment. Consent, safety, observed behavior, and
the people involved take priority over a score.

Run Porutham only or alongside Ashtakoota:

```sh
python scripts/guna_milan.py --chart-a chartA.json --chart-b chartB.json --method porutham10
python scripts/guna_milan.py --chart-a chartA.json --chart-b chartB.json --method both
```
