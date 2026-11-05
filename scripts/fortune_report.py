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
import argparse, json, pathlib, re, sys

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
    return {"mulank": mulank, "bhagyank": bhagyank, "name_total": total,
            "name_no": name_no, "soul": soul, "personality": pers,
            "grid_counts": counts, "missing": missing,
            "digits": "".join(str(d) for d in digits)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--request", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--brand", default="ASTRO NARAYAN PRAJAPATI")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    chart = json.loads(pathlib.Path(args.chart).read_text(encoding="utf-8"))
    req = json.loads(pathlib.Path(args.request).read_text(encoding="utf-8"))
    b = req["birth"]
    num = numerology(b["date"], args.name)
    j = chart["jyotisha"]; w = chart["western"]
    nak = j["moon_nakshatra"]
    safe = re.sub(r"[^A-Za-z0-9]+", "-", args.name.strip()).strip("-").upper()
    out = pathlib.Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    html_p = out / f"{safe}-Fortune-Report.html"
    pdf_p = out / f"{safe}-Fortune-Report.pdf"

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
<title>{args.name} — Fortune Report — {b['date']}</title>
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
<h1>FORTUNE<br>REPORT</h1>
<div style="color:#E8C766;letter-spacing:.25em">BY {args.brand}</div>
<div style="margin:26px auto 10px;padding:14px 44px;border:3px solid #E8C766;border-radius:999px;font-size:clamp(22px,3vw,34px)">{args.name}</div>
<div style="opacity:.95;line-height:1.8;margin-top:14px"><b>Birth:</b> {b['date']} · {b['time']} {b['timezone']} · {b['place']}<br>
<b>Lagna:</b> {j['ascendant']['sign']} {j['ascendant']['degree_in_sign']:.2f}° · <b>Moon:</b> {nak['name']} Pada {nak['pada']} · <b>Sun Sign:</b> {w['planets']['Sun']['sign']}<br>
<b>Report Date:</b> {req.get('as_of','')}</div>
</div>
<div class="toc"><b>INDEX:</b>
<a href="#disclaimer">Disclaimer</a><a href="#lucky">01 Lucky Things</a><a href="#numerology">02 Numerology</a>
<a href="#colour">03 Colour</a><a href="#health">05 Health</a><a href="#career">06 Career</a>
<a href="#grid">07 Grid</a><a href="#name">09 Name</a><a href="#future">10 Future</a>
<a href="#months">11 Month-wise</a><a href="#kundali">Kundali</a><a href="#lifepath">Life Path</a></div>

<section class="page" id="disclaimer"><h2>Disclaimer</h2>
<p>This report is a symbolic, traditional interpretive document prepared from the birth details supplied ({b['date']}, {b['time']} {b['timezone']}, {b['place']}). It is not professional medical, legal or financial advice. Numerological and astrological interpretations are traditional belief systems, presented for reflection, learning and entertainment. They are not scientifically established predictions and no outcome is guaranteed. Remedies, stones or rudraksh are traditional associations only and are not prescribed. Consult qualified professionals for health, education and finance decisions.</p></section>

<section class="page" id="lucky"><h2>Your Lucky Things</h2>
<table>
<tr><th>Name</th><td><b>{args.name}</b></td></tr>
<tr><th>Date of Birth</th><td>{b['date']}</td></tr>
<tr><th>Birth Time</th><td>{b['time']} (uncertainty ±{b.get('uncertainty_minutes','?')} min)</td></tr>
<tr><th>Place</th><td>{b['place']} — approx. {b['latitude']}°N, {b['longitude']}°E</td></tr>
<tr><th>Sun Sign (Tropical)</th><td>{w['planets']['Sun']['sign']}</td></tr>
<tr><th>Sidereal Sun</th><td>{j['planets']['Sun']['sign']} {j['planets']['Sun']['degree_in_sign']:.2f}° (Lahiri)</td></tr>
<tr><th>Lagna</th><td>{j['ascendant']['sign']} {j['ascendant']['degree_in_sign']:.2f}°</td></tr>
<tr><th>Moon / Nakshatra</th><td>{j['planets']['Moon']['sign']} · {nak['name']} Pada {nak['pada']}</td></tr>
<tr><th>Name Number</th><td>{num['name_no']} (raw sum {num['name_total']})</td></tr>
<tr><th>Mulank (Psychic Number)</th><td>{num['mulank']:02d}</td></tr>
<tr><th>Bhagyank (Destiny Number)</th><td>{num['bhagyank']}</td></tr>
<tr><th>Soul Urge / Personality</th><td>{num['soul']} / {num['personality']}</td></tr>
<tr><th>Lo Shu Digits</th><td>{num['digits']} · Missing: {", ".join(num['missing']) or "none"}</td></tr>
</table>
<p class="note">Full section prose (Mulank/Bhagyank effects, colours, career, health, grid analysis, month-wise themes, life-path) is written by the assistant following references/fortune-report.md, using only the numbers above and chart.json. Traditional items are listed for format completeness only and are not prescribed.</p>
</section>

<section class="page" id="numerology"><h2>Numerological Analysis</h2>
<p>Mulank <b>{num['mulank']}</b> (birth day reduced). Bhagyank <b>{num['bhagyank']}</b> (full birth date digit sum {num['digits']}). Name Number <b>{num['name_no']}</b> (raw sum {num['name_total']}). Soul Urge <b>{num['soul']}</b>, Personality <b>{num['personality']}</b>. Effects are given by the assistant per references/fortune-report.md; this file carries the computed facts.</p></section>

<section class="page" id="grid"><h2>Fortune Grid Analysis</h2>
<div class="grid3">{grid_html}</div>
<p>Digits {num['digits']}; counts {num['grid_counts']}; missing {num['missing']}.</p></section>

<section class="page" id="kundali"><h2>Kundali — Charts &amp; Tables</h2>
<h3>Western (tropical, Placidus)</h3><p>{planet_lines('western')}<br>ASC: {w['ascendant']['sign']} {w['ascendant']['degree_in_sign']:.2f}°</p>
<h3>Jyotisha (Lahiri, whole-sign)</h3><p>{planet_lines('jyotisha')}<br>Lagna: {j['ascendant']['sign']} {j['ascendant']['degree_in_sign']:.2f}° · Moon: {nak['name']} Pada {nak['pada']} · Tithi: {j['tithi_at_instant']['paksha']} {j['tithi_at_instant']['number']}</p>
<h3>Vimshottari Mahadashas</h3><table><tr><th>Lord</th><th>Period (UT)</th></tr>{md_rows}</table>
<p>Current: {chart['vimshottari']['current']['mahadasha']}–{chart['vimshottari']['current']['antardasha']} → {chart['vimshottari']['current']['end_utc'][:10]}</p>
<p>Full wheels: charts.html · Data: chart.json</p></section>

<section class="page" id="lifepath"><h2>Life-Path Appendix</h2>
<p>Career, Health, Family, Finance, Luck, Growth and Turning Points are written by the assistant from the placements above, following references/fortune-report.md — practical inference only, no medical, investment or irreversible-choice prescription.</p>
<p style="text-align:center;color:#8B1E1E">॥ शुभम् भवतु ॥<br><small>Prepared for <b>{args.name}</b> · {b['date']} · {b['place']} · By {args.brand}</small></p>
</section>
<div style="background:#1B1B4D;color:#fff;text-align:center;padding:14px">{args.name} · Fortune Report · {args.brand} · For reflection only</div>
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
                 Paragraph(f"BY {args.brand}",ParagraphStyle('by',parent=s_c,textColor=GOLD)),
                 Spacer(1,20), Paragraph(f"<b>{args.name}</b>",ParagraphStyle('pill',parent=s_c,fontSize=24)),
                 Spacer(1,30),
                 Paragraph(f"Birth: {b['date']} · {b['time']} {b['timezone']}<br/>{b['place']}<br/>Lagna: {j['ascendant']['sign']} · Moon: {nak['name']} Pada {nak['pada']} · Sun Sign: {w['planets']['Sun']['sign']}",s_c),
                 PageBreak(),
                 Paragraph("Disclaimer",s_h),
                 Paragraph(f"Symbolic, traditional interpretive document from {b['date']}, {b['time']}, {b['place']}. Not professional medical, legal or financial advice; not scientifically established prediction. Remedies/stones are traditional associations only and are not prescribed.",s_b),
                 Spacer(1,8),
                 Paragraph("Your Lucky Things",s_h)]
        rows = [["Name",args.name],["Date of Birth",b["date"]],["Time / Place",f"{b['time']} · {b['place']}"],
                ["Sun Sign",w["planets"]["Sun"]["sign"]],["Lagna / Moon",f"{j['ascendant']['sign']} / {nak['name']} Pada {nak['pada']}"],
                ["Mulank",str(num["mulank"])],["Bhagyank",str(num["bhagyank"])],["Name Number",str(num["name_no"])],
                ["Soul Urge / Personality",f"{num['soul']} / {num['personality']}"],
                ["Lo Shu Missing",", ".join(num["missing"]) or "none"]]
        t = Table([[Paragraph(f"<b>{a}</b>",s_b),Paragraph(x,s_b)] for a,x in rows],colWidths=[55*mm,115*mm])
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
