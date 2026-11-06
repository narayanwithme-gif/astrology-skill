#!/usr/bin/env python3
"""Lightweight PDF export. Language-dependent headings (en/hi/hinglish/mr/or)."""
import argparse, json
from pathlib import Path

HEAD = {
 "en": ["Kundali Reading","Birth Details","Lagna","Moon","Career","Health","Family","Finance","Luck","Growth","Turning Points"],
 "hi": ["कुंडली रिपोर्ट","जन्म विवरण","लग्न","चंद्र","करियर","स्वास्थ्य","परिवार","धन","भाग्य","विकास","जीवन मोड़"],
 "hinglish": ["Kundali Report","Janm Vivaran","Lagna","Chandra","Career","Swasthya","Parivar","Dhan","Bhagya","Vikas","Jeevan Mod"],
 "mr": ["कुंडली अहवाल","जन्म तपशील","लग्न","चंद्र","करिअर","आरोग्य","कुटुंब","वित्त","भाग्य","वाढ","वळणबिंदू"],
 "or": ["କୁଣ୍ଡଳୀ ରିପୋର୍ଟ","ଜନ୍ମ ବିବରଣୀ","ଲଗ୍ନ","ଚନ୍ଦ୍ର","କ୍ୟାରିୟର","ସ୍ୱାସ୍ଥ୍ୟ","ପରିବାର","ଅର୍ଥ","ଭାଗ୍ୟ","ବୃଦ୍ଧି","ଜୀବନ ମୋଡ଼"],
}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True); ap.add_argument("--request", required=True)
    ap.add_argument("--name", required=True); ap.add_argument("--lang", default="en",
                    choices=list(HEAD.keys()))
    ap.add_argument("--out", required=True); ap.add_argument("--reading", default=None)
    a = ap.parse_args()
    chart = json.loads(Path(a.chart).read_text(encoding="utf-8"))
    req = json.loads(Path(a.request).read_text(encoding="utf-8"))
    j = chart["jyotisha"]; nak = j["moon_nakshatra"]
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Try to register DejaVu/Noto for Devanagari/Odia; fall back to Helvetica
        font = "Helvetica"
        for cand in [r"C:\Windows\Fonts\Nirmala.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"]:
            if Path(cand).exists():
                try:
                    pdfmetrics.registerFont(TTFont("Uni", cand)); font = "Uni"; break
                except Exception: pass
        st = getSampleStyleSheet()
        h = ParagraphStyle("h", parent=st["Heading1"], fontName=font)
        b = ParagraphStyle("b", parent=st["BodyText"], fontName=font, leading=14)
        t = ParagraphStyle("t", parent=st["Title"], fontName=font)
        H = HEAD[a.lang]
        story = [Paragraph(f"{H[0]} — {a.name}", t), Spacer(1,12),
                 Paragraph(f"{H[1]}: {req['birth']['date']} {req['birth']['time']} {req['birth']['place']}", b),
                 Paragraph(f"{H[2]}: {j['ascendant']['sign']} {j['ascendant']['degree_in_sign']:.2f}° · {H[3]}: {nak['name']} Pada {nak['pada']}", b)]
        for lbl in H[4:]:
            story += [Spacer(1,8), Paragraph(lbl, h),
                      Paragraph("See reading.md (same data, chosen template language). Practical inference only; no medical/finance prescription.", b)]
        if a.reading and Path(a.reading).exists():
            txt = Path(a.reading).read_text(encoding="utf-8")[:4000].replace("&", "&amp;").replace("<", "&lt;")
            story += [Spacer(1,12), Paragraph(txt.replace("\n", "<br/>"), b)]
        SimpleDocTemplate(a.out, pagesize=A4, title=f"{a.name} Kundali").build(story)
        print(f"written: {a.out} lang={a.lang} font={font}")
    except ImportError as e:
        print(f"reportlab missing ({e}); install: pip install reportlab pillow")
        return

if __name__ == "__main__":
    main()
