# Output templates (language-dependent)

Select template by user language preference. Default `en`. Never use a template language the user didn't ask for.

| Code | Language | Headings |
|---|---|---|
| `en` | English | Kundali Reading, Birth Details, Lagna, Moon, Career, Health, Family, Finance, Luck, Growth, Turning Points |
| `hi` | Hindi (Devanagari) | कुंडली रिपोर्ट, जन्म विवरण, लग्न, चंद्र, करियर, स्वास्थ्य, परिवार, धन, भाग्य, विकास, जीवन मोड़ |
| `hinglish` | Hinglish (Latin Hindi) | Kundali Report, Janm Vivaran, Lagna, Chandra, Career, Swasthya, Parivar, Dhan, Bhagya, Vikas, Jeevan Mod |
| `mr` | Marathi (Devanagari) | कुंडली अहवाल, जन्म तपशील, लग्न, चंद्र, करिअर, आरोग्य, कुटुंब, वित्त, भाग्य, वाढ, वळणबिंदू |
| `or` | Odia | କୁଣ୍ଡଳୀ ରିପୋର୍ଟ, ଜନ୍ମ ବିବରଣୀ, ଲଗ୍ନ, ଚନ୍ଦ୍ର, କ୍ୟାରିୟର, ସ୍ୱାସ୍ଥ୍ୟ, ପରିବାର, ଅର୍ଥ, ଭାଗ୍ୟ, ବୃଦ୍ଧି, ଜୀବନ ମୋଡ଼ |

## Usage
`python scripts/pdf_export.py --chart chart.json --request request.json --name "FULL NAME" --lang en|hi|hinglish|mr|or --out report.pdf --reading reading.md`

- PDF is lightweight (reportlab). Devanagari uses Noto/DejaVu if present, else falls back and notes missing glyphs.
- Same data + headings in every language; interpretation prose follows the chosen template language, numbers/tables are identical.
- Fortune Report (`fortune_report.py`) accepts `--lang` and applies these headings to cover/Index/Lucky Things/Life-Path.

## Rules
- Never invent a translation for a technique name; transliterate if unsure and flag it.
- Safety boundaries (no remedies for minors, no health/finance prediction) apply in every language.
