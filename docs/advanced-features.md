# Advanced Astrology Features Guide

This document provides detailed documentation for the advanced astrology modules in astrology-skill.

## Table of Contents

1. [Composite and Relationship Charts](#composite-and-relationship-charts)
2. [Progressions and Returns](#progressions-and-returns)
3. [Relocation Charts](#relocation-charts)
4. [Shadbala (Six-fold Strength)](#shadbala-six-fold-strength)
5. [Ashtakavarga (Bindu System)](#ashtakavarga-bindu-system)
6. [KP and Jaimini Systems](#kp-and-jaimini-systems)

---

## Composite and Relationship Charts

**Module:** `scripts/composite_charts.py`

### Midpoint Composite Chart

The midpoint composite calculates the average of two natal charts. It's useful for understanding the "relationship personality" — what the partnership together creates.

```python
from composite_charts import midpoint_chart

# Calculate midpoint composite
composite = midpoint_chart(chart_a, chart_b, latitude, longitude, settings)
```

### Davison Relationship Chart

The Davison chart finds the midpoint in time and space between two births. It represents the "joint entity" of the relationship.

```python
from composite_charts import davison_chart

davison = davison_chart(birth_dt_a, birth_dt_b, latitude, longitude, settings)
```

### Synastry Aspects

Calculate how one person's planets aspect another person's chart.

```python
from composite_charts import synastry_aspects

aspects = synastry_aspects(chart_a, chart_b, orb=6)
```

---

## Progressions and Returns

**Module:** `scripts/progressions.py`

### Secondary Progressions

Day-for-a-year method: one day after birth equals one year of life.

```python
from progressions import secondary_progressions

prog = secondary_progressions(birth_dt, target_dt, lat, lon, settings)
```

### Solar Return

Calculate the chart for when the transiting Sun returns to its natal position.

```python
from progressions import solar_return

sr = solar_return(birth_dt, year, lat, lon, settings)
```

### Lunar Return

Find when the transiting Moon returns to its natal position.

```python
from progressions import lunar_return

lr = lunar_return(birth_dt, target_month, lat, lon, settings)
```

---

## Relocation Charts

**Module:** `scripts/relocation.py`

### Locality Chart

Recalculate the same birth moment at a new geographic location. Planet positions remain the same; only angles and houses change.

```python
from relocation import relocation_chart

relocated = relocation_chart(natal_chart_data, new_lat, new_lon, settings)
```

---

## Shadbala (Six-fold Strength)

**Module:** `scripts/shadbala.py`

Shadbala is the six-fold strength system from the Brihat Par Hora Shastra (BPHS).

### Components

| Component | Description | Max Points |
|-----------|-------------|------------|
| Sthana Bala | Positional strength (sign placement) | 60 |
| Dig Bala | Directional strength (houses) | 60 |
| Cheshta Bala | Motional strength (retrograde) | 60 |
| Kala Bala | Temporal strength (day/night) | 60 |
| Uccha Bala | Exaltation strength | 60 |
| Naisa Bala | Aspect strength | 60 |
| Drik Bala | Benefic aspect strength | 60 |

### Usage

```python
from shadbala import calculate_shadbala

strength = calculate_shadbala(chart_data)
```

Each planet gets a total score. Traditional interpretation thresholds:
- **Purnabala**: > 60% of total possible
- **Madhyabala**: 40-60%
- **Durbala**: < 40%

---

## Ashtakavarga (Bindu System)

**Module:** `scripts/ashtakavarga.py`

Ashtakavarga assigns bindu (points) to each sign based on planetary strength.

### Types

- **Bhinnashtakavarga**: Individual planet scores per sign
- **Sarvashtakavarga**: Total scores per sign (sum of all planets)
- **Samudaya**: Planetary strength by house
- **Kudumba**: Planetary strength by sign

### Usage

```python
from ashtakavarga import calculate_ashtakavarga

av = calculate_ashtakavarga(chart_data)
```

Traditional Sarvashtakavarga interpretation:
- **28+**: Very strong sign
- **24-27**: Strong
- **20-23**: Average
- **< 20**: Weak

---

## KP and Jaimini Systems

**Module:** `scripts/kp_system.py`

### KP (Krishnamurti Paddhati)

KP uses a different subdivision system based on nakshatras and their sub-portions.

```python
from kp_system import calculate_kp

kp = calculate_kp(chart_data)
```

Key KP concepts:
- **Star/Sign Lord**: Which nakshatra and sign governs a position
- **Sub Lord**: 1/9 subdivision of a star portion
- **Sub-Sub Lord**: Further 1/9 subdivision
- **Ruling Planet**: Used for timing and predictions
- **Cuspal Interlink**: Which houses are connected via cusp sub-lords

### Jaimini

Jaimini uses a different karma/strength system.

```python
from kp_system import calculate_jaimini

jm = calculate_jaimini(chart_data, birth_jd, as_of_dt)
```

Jaimini features:
- **7-Karaka Scheme**: AK (Atmakaraka) through SK (Shatru Karaka)
- **Chara Dasha**: Variable-length periods based on karakas
- **Rashi Drishti**: Special aspects based on sign type

---

## Complete Example

```python
import json
from datetime import datetime

# Load a chart
with open('chart.json') as f:
    chart = json.load(f)

# Calculate multiple systems
from shadbala import calculate_shadbala
from ashtakavarga import calculate_ashtakavarga
from kp_system import calculate_jaimini

results = {
    'shadbala': calculate_shadbala(chart),
    'ashtakavarga': calculate_ashtakavarga(chart),
    'jaimini': calculate_jaimini(chart)
}

print(json.dumps(results, indent=2))
```

---

## Limitations

These advanced modules are early-stage implementations:
- Cross-check against a trusted reference before publishing
- Test vectors are not yet fully validated
- Some simplifications may differ from traditional calculations
- KP and Jaimini require Krishnamurti ayanamsha settings