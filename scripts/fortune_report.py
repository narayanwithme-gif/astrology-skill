#!/usr/bin/env python3
"""Generate a branded Fortune Report (HTML + PDF) from chart.json + request.json.

Usage:
  python fortune_report.py --chart chart.json --request request.json \
      --name "FULL NAME" --brand "BRAND" --out-dir DIR

Numerology is derived from the request birth date and --name (never copied
from a sample report). Chart facts come from chart.json. The HTML is a single
self-contained file; the PDF uses reportlab + pillow. See
references/fortune-report.md for the contract.
"""
from __future__ import annotations
import argparse, html as _h, json, pathlib, re, sys
from xml.sax.saxutils import escape as _xml_escape

def H(x):
    """Escape user text for HTML context."""
    return _h.escape(str(x), quote=True)

def esc(x):
    """Escape user text for ReportLab Paragraph (XML) context."""
    return _xml_escape(str(x))

def reduce9(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

def name_number(name):
    vals = {c: reduce9(ord(c) - 64) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    total = sum(vals.get(c, 0) for c in name.upper() if c.isalpha())
    return total, reduce9(total)

def vowels_consonants(name):
    v = sum(reduce9(ord(c) - 64) for c in name.upper() if c in "AEIOU")
    c = sum(reduce9(ord(c) - 64) for c in name.upper() if c.isalpha() and c not in "AEIOU")
    return reduce9(v), reduce9(c)

def numerology(birth_date, name):
    dd, mm, yyyy = birth_date.split("-")
    mulank = reduce9(int(dd))
    bhagyank = reduce9(sum(int(c) for c in (dd + mm + yyyy)))
    total, name_no = name_number(name)
    soul, pers = vowels_consonants(name)
    digits = [int(c) for c in (dd + mm + yyyy) if c != "0"]
    counts = {str(d): digits.count(d) for d in set(digits)}
    missing = [str(d) for d in range(1, 10) if str(d) not in counts]
    # Kua (Feng Shui): year digits sum -> s; step = 4 male / 5 female; s>9 -> s-9; Kua = 10-step; female 5->8
    s = reduce9(sum(int(c) for c in yyyy))
    # caller passes gender via global? keep pure: return s, Kua computed by caller
    kua_male = 10 - (4 + s if s <= 9 else 4 + s - 9)
    kua_female = 10 - (5 + s if s <= 9 else 5 + s - 9)
    if kua_female == 5:
        kua_female = 8
    return {"mulank": mulank, "bhagyank": bhagyank, "name_total": total,
            "name_no": name_no, "soul": soul, "personality": pers,
            "grid_counts": counts, "missing": missing,
            "digits": "".join(str(d) for d in digits),
            "kua_male": kua_male, "kua_female": kua_female}

KUA_DIRS = {1: ("South", "North", "East", "South-East"), 2: ("South-West", "North-West", "West", "North-East"),
            3: ("East", "South", "North", "South-West"), 4: ("South-East", "East", "South", "North"),
            6: ("North-West", "South-West", "West", "North-East"), 7: ("West", "North-West", "North", "South-East"),
            8: ("North-East", "South-West", "North-West", "West"), 9: ("North", "South", "East", "South-West")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--request", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--brand", default="ASTRO NARAYAN PRAJAPATI")
    ap.add_argument("--gender", default="", help="female|male (for Kua); default: male")
    ap.add_argument("--lang", default="en", choices=["en","hi","hinglish","mr","or"], help="Template language (references/templates.md)")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    chart = json.loads(pathlib.Path(args.chart).read_text(encoding="utf-8"))
    req = json.loads(pathlib.Path(args.request).read_text(encoding="utf-8"))
    b = req["birth"]
    num = numerology(b["date"], args.name)
    # Kua by gender
    eff_gender = (args.gender or req.get("gender", "")).lower()
    kua = num["kua_female"] if eff_gender.startswith("f") else num["kua_male"]
    kua_basis = "female" if eff_gender.startswith("f") else "male (default; set --gender to override)"
    # Lang headings (references/templates.md)
    TPL = {
      "en": ["FORTUNE REPORT","Your Lucky Things","Numerological Analysis","Fortune Grid Analysis","Life-Path Appendix"],
      "hi": ["कुंडली रिपोर्ट","आपके शुभ अंक","अंक शास्त्र विश्लेषण","लो शु ग्रिड विश्लेषण","जीवन मार्ग परिशिष्ट"],
      "hinglish": ["FORTUNE REPORT","Aapke Lucky Things","Numerology Analysis","Fortune Grid Analysis","Life-Path Appendix"],
      "mr": ["कुंडली अहवाल","तुमच्या शुभ गोष्टी","अंकशास्त्र विश्लेषण","लो शु ग्रिड विश्लेषण","जीवन मार्ग परिशिष्ट"],
      "or": ["ଭାଗ୍ୟ ରିପୋର୍ଟ","ଆପଣଙ୍କ ଶୁଭ ଜିନିଷ","ଅଙ୍କଶାସ୍ତ୍ର ବିଶ୍ଳେଷଣ","ଲୋ ଶୁ ଗ୍ରିଡ୍ ବିଶ୍ଳେଷଣ","ଜୀବନ ପଥ ପରିଶିଷ୍ଟ"],
    }
    TH = TPL.get((args.lang or "en").lower(), TPL["en"])
    j = chart["jyotisha"]; w = chart["western"]
    nak = j["moon_nakshatra"]
    safe = re.sub(r"[^A-Za-z0-9]+", "-", args.name.strip()).strip("-").upper()
    out = pathlib.Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    html_p = out / f"{safe}-Fortune-Report.html"
    pdf_p = out / f"{safe}-Fortune-Report.pdf"

    # Escaped copies for HTML (all user-supplied text) and ReportLab (XML) contexts
    E_NAME, E_BRAND = H(args.name), H(args.brand)
    E_DATE, E_TIME, E_TZ, E_PLACE = H(b["date"]), H(b["time"]), H(b["timezone"]), H(b["place"])
    E_ASOF = H(req.get("as_of", ""))
    E_JUP_SIGN, E_W_SUN = H(j["planets"]["Sun"]["sign"]), H(w["planets"]["Sun"]["sign"])
    E_J_ASC, E_W_ASC = H(j["ascendant"]["sign"]), H(w["ascendant"]["sign"])
    E_NAK, E_PAKSHA = H(nak["name"]), H(j["tithi_at_instant"]["paksha"])
    kua_dirs = KUA_DIRS.get(kua, ("—",) * 4)
    E_KUA_LBL = H(kua_basis)
    # --- HTML (purple cover + parchment, 16 sections + Kundali + Life-Path) ---
    # The full section copy is generated from the computed numerology and
    # chart facts below; keep it original, never copied from a sample report.
    def planet_lines(sec):
        return "<br>".join(f"{k}: {v['sign']} {v['degree_in_sign']:.2f}° H{v['house']}"
                           for k, v in chart[sec]["planets"].items())
    md_rows = "".join(f"<tr><td>{m['lord']}</td><td>{m['start_utc'][:10]} → {m['end_utc'][:10]}</td></tr>"
                      for m in chart["vimshottari"]["mahadashas"])
    grid_pos = {"4":0,"9":1,"2":2,"3":3,"5":4,"7":5,"8":6,"1":7,"6":8}
    cells = [""] * 9
    for d, c in num["grid_counts"].items():
        i = grid_pos[d]; cells[i] = f"{d}<br><small>{d*c}</small>"
    grid_html = "".join(f"<div>{c}</div>" for c in cells)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{E_NAME} — Fortune Report — {E_DATE}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--purple:#2B0A4A;--gold:#C9A227;--parch:#F3E6C3;--ink:#241A12}}
*{{box-sizing:border-box}} body{{margin:0;background:#1e0738;font-family:Georgia,serif;color:var(--ink)}}
.cover{{min-height:100vh;background:linear-gradient(180deg,#2B0A4A,#5A1A7A 55%,#8A3A6B);color:#fff;text-align:center;padding:48px 22px 36px;border:6px solid #C9A227;margin:18px}}
.cover h1{{font-size:clamp(44px,8vw,96px);letter-spacing:.06em;margin:26px 0 6px}}
.page{{background:radial-gradient(circle at 20% 10%,#fff8e6,var(--parch) 45%,#ead9a8);margin:22px auto;max-width:980px;padding:56px 46px 70px;border-top:10px solid #1B1B4D;border-bottom:10px solid #C9A227}}
h2{{font-size:1.9rem;border-bottom:3px solid #8B1E1E;display:inline-block;padding-bottom:6px}}
table{{width:100%;border-collapse:collapse;background:#FFF8DC;margin:16px 0}}
th,td{{border:2px solid #C9A227;padding:13px 14px;text-align:left;vertical-align:top}}
th{{background:#FFF1B8;width:42%}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;max-width:420px;margin:16px auto;border:3px solid #C9A227}}
.grid3 div{{border:1px solid #C9A227;min-height:88px;display:flex;align-items:center;justify-content:center;font-size:1.6rem;font-weight:bold;color:#8B1E1E;background:#FFF8DC}}
.note{{background:#fff;border-left:6px solid #C9A227;padding:14px 18px;margin:16px 0}}
.toc{{background:#2B0A4A;color:#fff;margin:18px auto;max-width:980px;padding:14px 20px;border-radius:12px}}
.toc a{{color:#E8C766;text-decoration:none;border:1px solid #E8C766;border-radius:999px;padding:4px 10px;font-size:.85rem;margin-right:6px}}
@media print{{.toc{{display:none}}.page{{box-shadow:none;margin:0;max-width:none;page-break-after:always}}}}
</style></head><body>
<div class="cover">
<div style="color:#E8C766">॥ ॐ श्री गणेशाय नमः ॥</div>
<div style="letter-spacing:.3em;color:#E8C766;margin-top:18px">YOUR</div>
<h1>{TH[0]}</h1>
<div style="color:#E8C766;letter-spacing:.25em">BY {E_BRAND}</div>
<div style="margin:26px auto 10px;padding:14px 44px;border:3px solid #E8C766;border-radius:999px;font-size:clamp(22px,3vw,34px)">{E_NAME}</div>
<div style="opacity:.95;line-height:1.8;margin-top:14px"><b>Birth:</b> {E_DATE} · {E_TIME} {E_TZ} · {E_PLACE}<br>
<b>Lagna:</b> {E_J_ASC} {j['ascendant']['degree_in_sign']:.2f}° · <b>Moon:</b> {E_NAK} Pada {nak['pada']} · <b>Sun Sign:</b> {E_W_SUN}<br>
<b>Report Date:</b> {E_ASOF}</div>
</div>
<div class="toc"><b>INDEX:</b>
<a href="#disclaimer">Disclaimer</a><a href="#lucky">01 Lucky Things</a><a href="#numerology">02 Numerology</a>
<a href="#colour">03 Colour</a><a href="#health">05 Health</a><a href="#career">06 Career</a>
<a href="#grid">07 Grid</a><a href="#name">09 Name</a><a href="#future">10 Future</a>
<a href="#months">11 Month-wise</a><a href="#kundali">Kundali</a><a href="#lifepath">Life Path</a></div>

<section class="page" id="disclaimer"><h2>Disclaimer</h2>
<p>This report is a symbolic, traditional interpretive document prepared from the birth details supplied ({E_DATE}, {E_TIME} {E_TZ}, {E_PLACE}). It is not professional medical, legal or financial advice. Numerological and astrological interpretations are traditional belief systems, presented for reflection, learning and entertainment. They are not scientifically established predictions and no outcome is guaranteed. Remedies, stones or rudraksh are traditional associations only and are not prescribed. Consult qualified professionals for health, education and finance decisions.</p></section>

<section class="page" id="lucky"><h2>{TH[1]}</h2>
<table>
<tr><th>Name</th><td><b>{E_NAME}</b></td></tr>
<tr><th>Date of Birth</th><td>{E_DATE}</td></tr>
<tr><th>Birth Time</th><td>{E_TIME} (uncertainty ±{b.get('uncertainty_minutes','?')} min)</td></tr>
<tr><th>Place</th><td>{E_PLACE} — approx. {b['latitude']}°N, {b['longitude']}°E</td></tr>
<tr><th>Sun Sign (Tropical)</th><td>{E_W_SUN}</td></tr>
<tr><th>Sidereal Sun</th><td>{E_JUP_SIGN} {j['planets']['Sun']['degree_in_sign']:.2f}° (Lahiri)</td></tr>
<tr><th>Lagna</th><td>{E_J_ASC} {j['ascendant']['degree_in_sign']:.2f}°</td></tr>
<tr><th>Moon / Nakshatra</th><td>{j['planets']['Moon']['sign']} · {E_NAK} Pada {nak['pada']}</td></tr>
<tr><th>Kua Number</th><td>{kua} ({E_KUA_LBL})</td></tr>
<tr><th>Name Number</th><td>{num['name_no']} (raw sum {num['name_total']})</td></tr>
<tr><th>Mulank (Psychic Number)</th><td>{num['mulank']:02d}</td></tr>
<tr><th>Bhagyank (Destiny Number)</th><td>{num['bhagyank']}</td></tr>
<tr><th>Soul Urge / Personality</th><td>{num['soul']} / {num['personality']}</td></tr>
<tr><th>Lo Shu Digits</th><td>{num['digits']} · Missing: {", ".join(num['missing']) or "none"}</td></tr>
</table>
<p class="note">Full section prose (Mulank/Bhagyank effects, colours, career, health, grid analysis, month-wise themes, life-path) is written by the assistant following references/fortune-report.md, using only the numbers above and chart.json. Traditional items are listed for format completeness only and are not prescribed.</p>
</section>

<section class="page" id="numerology"><h2>{TH[2]}</h2>
<p>Mulank <b>{num['mulank']}</b> (birth day reduced). Bhagyank <b>{num['bhagyank']}</b> (full birth date digit sum {num['digits']}). Name Number <b>{num['name_no']}</b> (raw sum {num['name_total']}). Soul Urge <b>{num['soul']}</b>, Personality <b>{num['personality']}</b>. Effects are given by the assistant per references/fortune-report.md; this file carries the computed facts.</p></section>

<section class="page" id="grid"><h2>{TH[3]}</h2>
<div class="grid3">{grid_html}</div>
<p>Digits {num['digits']}; counts {num['grid_counts']}; missing {num['missing']}.</p></section>

<section class="page" id="kundali"><h2>Kundali — Charts &amp; Tables</h2>
<h3>Western (tropical, Placidus)</h3><p>{planet_lines('western')}<br>ASC: {w['ascendant']['sign']} {w['ascendant']['degree_in_sign']:.2f}°</p>
<h3>Jyotisha (Lahiri, whole-sign)</h3><p>{planet_lines('jyotisha')}<br>Lagna: {E_J_ASC} {j['ascendant']['degree_in_sign']:.2f}° · Moon: {E_NAK} Pada {nak['pada']} · Tithi: {E_PAKSHA} {j['tithi_at_instant']['number']}</p>
<h3>Vimshottari Mahadashas</h3><table><tr><th>Lord</th><th>Period (UT)</th></tr>{md_rows}</table>
<p>Current: {chart['vimshottari']['current']['mahadasha']}–{chart['vimshottari']['current']['antardasha']} → {chart['vimshottari']['current']['end_utc'][:10]}</p>
<p>Full wheels: charts.html · Data: chart.json</p></section>

<section class="page" id="lifepath"><h2>{TH[4]}</h2>
<p>Career, Health, Family, Finance, Luck, Growth and Turning Points are written by the assistant from the placements above, following references/fortune-report.md — practical inference only, no medical, investment or irreversible-choice prescription.</p>
<p style="text-align:center;color:#8B1E1E">॥ शुभम् भवतु ॥<br><small>Prepared for <b>{E_NAME}</b> · {E_DATE} · {E_PLACE} · By {E_BRAND}</small></p>
</section>
<div style="background:#1B1B4D;color:#fff;text-align:center;padding:14px">{E_NAME} · Fortune Report · {E_BRAND} · For reflection only</div>
</body></html>
"""
    html_p.write_text(html, encoding="utf-8")

    # --- PDF ---
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor, white
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        PURPLE = HexColor("#2B0A4A"); GOLD = HexColor("#C9A227"); PARCH = HexColor("#F3E6C3")
        st = getSampleStyleSheet()
        s_t = ParagraphStyle('t', parent=st['Title'], fontSize=42, textColor=white, leading=48)
        s_h = ParagraphStyle('h', parent=st['Heading1'], fontSize=20, textColor=PURPLE)
        s_b = ParagraphStyle('b', parent=st['BodyText'], fontSize=10, leading=14)
        s_c = ParagraphStyle('c', parent=s_b, alignment=1, textColor=white)
        def cover(canvas, doc):
            canvas.saveState(); canvas.setFillColor(PURPLE); canvas.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
            canvas.setStrokeColor(GOLD); canvas.setLineWidth(3); canvas.rect(18,18,A4[0]-36,A4[1]-36,fill=0,stroke=1); canvas.restoreState()
        def hdr(canvas, doc):
            canvas.saveState(); canvas.setFillColor(PARCH); canvas.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
            canvas.setFillColor(PURPLE); canvas.rect(0,A4[1]-14*mm,A4[0],14*mm,fill=1,stroke=0)
            canvas.setFillColor(white); canvas.setFont("Helvetica",8)
            canvas.drawCentredString(A4[0]/2,A4[1]-9*mm,f"{args.name} · Fortune Report · {args.brand}")
            canvas.setFillColor(PURPLE); canvas.rect(0,0,A4[0],12*mm,fill=1,stroke=0)
            canvas.setFillColor(white); canvas.drawCentredString(A4[0]/2,5*mm,f"Page {doc.page} · For reflection only")
            canvas.restoreState()
        story = [Spacer(1,90), Paragraph("॥ ॐ श्री गणेशाय नमः ॥",s_c), Spacer(1,30), Paragraph("YOUR",s_c),
                 Paragraph("FORTUNE REPORT",ParagraphStyle('ct',parent=s_t,alignment=1)),
                 Paragraph(f"BY {esc(args.brand)}",ParagraphStyle('by',parent=s_c,textColor=GOLD)),
                 Spacer(1,20), Paragraph(f"<b>{esc(args.name)}</b>",ParagraphStyle('pill',parent=s_c,fontSize=24)),
                 Spacer(1,30),
                 Paragraph(f"Birth: {esc(b['date'])} · {esc(b['time'])} {esc(b['timezone'])}<br/>{esc(b['place'])}<br/>Lagna: {esc(j['ascendant']['sign'])} · Moon: {esc(nak['name'])} Pada {nak['pada']} · Sun Sign: {esc(w['planets']['Sun']['sign'])}",s_c),
                 PageBreak(),
                 Paragraph("Disclaimer",s_h),
                 Paragraph(f"Symbolic, traditional interpretive document from {b['date']}, {b['time']}, {b['place']}. Not professional medical, legal or financial advice; not scientifically established prediction. Remedies/stones are traditional associations only and are not prescribed.",s_b),
                 Spacer(1,8),
                 Paragraph("Your Lucky Things",s_h)]
        rows = [["Name",args.name],["Date of Birth",b["date"]],["Time / Place",f"{b['time']} · {b['place']}"],
                ["Sun Sign",w["planets"]["Sun"]["sign"]],["Lagna / Moon",f"{j['ascendant']['sign']} / {nak['name']} Pada {nak['pada']}"],
                ["Mulank",str(num["mulank"])],["Bhagyank",str(num["bhagyank"])],["Name Number",str(num["name_no"])],
                ["Soul Urge / Personality",f"{num['soul']} / {num['personality']}"],
                ["Kua Number",str(kua)],
                ["Lo Shu Missing",", ".join(num["missing"]) or "none"]]
        t = Table([[Paragraph(f"<b>{esc(a)}</b>",s_b),Paragraph(esc(x),s_b)] for a,x in rows],colWidths=[55*mm,115*mm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),PARCH),('GRID',(0,0),(-1,-1),1,GOLD),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story += [t, Spacer(1,8), Paragraph("Kundali Summary",s_h),
                  Paragraph(f"Jyotisha Lagna {j['ascendant']['sign']} {j['ascendant']['degree_in_sign']:.2f}°. D9 ASC {j['D9']['ascendant']['sign']}, D10 ASC {j['D10']['ascendant']['sign']}. Full wheels in charts.html; data in chart.json.",s_b),
                  Paragraph("Life-Path Appendix",s_h),
                  Paragraph("Career, Health, Family, Finance, Luck, Growth and Turning Points are written in the HTML report from these placements — practical inference only, no medical, investment or irreversible-choice prescription.",s_b)]
        doc = SimpleDocTemplate(str(pdf_p),pagesize=A4,topMargin=18*mm,bottomMargin=18*mm,leftMargin=18*mm,rightMargin=18*mm,
                                title=f"{args.name} Fortune Report",author=args.brand)
        doc.build(story,onFirstPage=cover,onLaterPages=hdr)
    except ImportError as e:
        print(f"PDF skipped (missing reportlab/pillow: {e}). HTML written to {html_p}", file=sys.stderr)
        return

    print(f"written: {html_p}\nwritten: {pdf_p}")

if __name__ == "__main__":
    main()
