# Changelog

## [1.3.0] - 2026-11-06
- **Guna Milan 36**: deterministic Ashtakoota (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) in `scripts/guna_milan.py`, with modern 0–100 synastry alongside. CLI: `guna_milan.py --chart-a A.json --chart-b B.json`
- **Selectable ayanamsha**: `lahiri`, `kp` (Krishnamurti alias), `raman` in `settings.ayanamsha`; KP practitioners no longer need a separate tool
- **Multilingual + PDF**: `references/templates.md` (English, Hindi/Hinglish, Marathi, Odia) driven by user language preference; `fortune_report.py --lang` and lightweight `scripts/pdf_export.py` for marketplace-ready listing (Agensi x Narayan)

## [1.2.0] - 2026-11-05
- Fortune Report mode (branded HTML+PDF, Kua, Lo Shu Grid, HTML/XML escaping)
- Deterministic reading generator (byte-identical from chart.json)
- Dual-engine validation harness and external-vector test suite
- Panchanga / transit-event-search and Ashtakavarga/Shadbala/KP-Jaimini specs
- Docs: validation report, conventions review, golden tests (22+)

Known limitations: external Jagannatha Hora / Drik Panchang vectors pending;
practitioner review pending; Shadbala/Ashtakavarga/KP-Jaimini not implemented.
