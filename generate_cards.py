#!/usr/bin/env python3
"""Render self-contained animated SVG cards for a GitHub profile README."""
import os, json, base64, subprocess, sys, urllib.request, calendar
from pathlib import Path
from datetime import date, timedelta
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
OUT, DATA = ROOT / "cards", ROOT / "data/contributions.json"
USER = os.getenv("GITHUB_USERNAME", "jahnavist04")
NAME = os.getenv("DISPLAY_NAME", "Jahnavi")
TAGLINE = os.getenv("TAGLINE", "Data Science engineer building useful things with code.")
PORTRAIT = os.getenv("PORTRAIT_URL", "").strip()
PRIMARY, MID, DARK = "#6B0000", "#8B1A1A", "#3D0000"
PANEL, FG, MUTED, ACCENT = "#1B1517", "#F7F1F2", "#B9A9AD", "#DFA9B4"
STATIC = os.getenv("STATIC", "0").lower() in ("1", "true", "yes")
REPOS = [
    ("CompanyBrain", "RAG-powered Q&A for company documents", "FastAPI · LangChain · ChromaDB · React"),
    ("GHOST Protocol", "Monitoring AI systems for unusual behaviour", "Python · scikit-learn · Isolation Forest"),
    ("EMOTEX", "Facial expression analysis and visual reporting", "TensorFlow.js · face-api · JavaScript"),
    ("SignBridge", "A sign-language translation project", "Flutter · HTML"),
]
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/firacode/FiraCode%5Bwght%5D.ttf"
FONT_FILE, FONT_WOFF = ROOT / "assets/FiraCode[wght].ttf", ROOT / "assets/FiraCode-subset.woff"
FONT_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:!?@#&()[]{}+-=*/_'\"<>%|→—·"

def x(v): return escape(str(v), {'"': '&quot;'})

def get_days():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    if "days" in raw:
        days = [{"date": z["date"], "count": int(z.get("count", 0))} for z in raw["days"]]
        total = int(raw.get("totalContributions", sum(z["count"] for z in days)))
    else:
        cal = raw.get("data", raw).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {})
        days = [{"date": d["date"], "count": int(d["contributionCount"])} for w in cal.get("weeks", []) for d in w.get("contributionDays", [])]
        total = int(cal.get("totalContributions", sum(z["count"] for z in days)))
    return sorted(days, key=lambda z: z["date"]), total

def font_data():
    try:
        (ROOT / "assets").mkdir(exist_ok=True)
        if not FONT_FILE.exists():
            req = urllib.request.Request(FONT_URL, headers={"User-Agent": "profile-card-generator"})
            FONT_FILE.write_bytes(urllib.request.urlopen(req, timeout=25).read())
        if not FONT_WOFF.exists() or FONT_WOFF.stat().st_mtime < FONT_FILE.stat().st_mtime:
            subprocess.run(["pyftsubset", str(FONT_FILE), f"--output-file={FONT_WOFF}",
                "--flavor=woff", f"--text={FONT_CHARS}", "--layout-features=*"],
                check=True, stdout=subprocess.DEVNULL)
        return base64.b64encode(FONT_WOFF.read_bytes()).decode()
    except Exception as err:
        print(f"Fira Code subset unavailable; using monospace fallback ({err})", file=sys.stderr)
        return ""

def start(w, h, font, delay=0):
    face = f"@font-face{{font-family:FiraCode;src:url(data:font/woff;base64,{font}) format('woff');font-weight:100 900}}" if font else ""
    motion = "" if STATIC else f'''
      @keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
      @keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
      .enter{{opacity:0;animation:rise .8s ease-out {delay}s forwards}}
      .twinkle{{animation:pulse 2.8s ease-in-out {delay+.5}s infinite}}
      @media(prefers-reduced-motion:reduce){{.enter,.twinkle{{animation:none!important;opacity:1!important;transform:none!important}}.motion-only{{display:none!important}}}}
    '''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
    <defs><linearGradient id="brand" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{PRIMARY}"/><stop offset=".55" stop-color="{MID}"/><stop offset="1" stop-color="{DARK}"/></linearGradient>
    <style>{face} text{{font-family:FiraCode,'SFMono-Regular',Consolas,monospace}}{motion}</style></defs>'''

def end(): return "</svg>"
def box(w,h,r=20): return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="{PANEL}" stroke="#55353D"/>'
def save(name, svg):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(svg+end(), encoding="utf-8")

def hero(font):
    s=start(1000,250,font,0)+box(1000,250)
    s+=f'<rect x="1" y="1" width="998" height="248" rx="20" fill="url(#brand)" opacity=".3"/>'
    s+=f'<g class="enter"><text x="48" y="65" fill="{ACCENT}" font-size="17" letter-spacing="3">@{x(USER)}</text><text x="48" y="137" fill="{FG}" font-size="58" font-weight="700">{x(NAME)}</text><text x="51" y="181" fill="{MUTED}" font-size="19">{x(TAGLINE)}</text><text x="51" y="220" fill="{ACCENT}" font-size="14">BUILDING · LEARNING · SHIPPING</text></g>'
    if PORTRAIT:
        s+=f'<defs><clipPath id="clip"><circle cx="865" cy="125" r="77"/></clipPath></defs><image href="{x(PORTRAIT)}" x="788" y="48" width="154" height="154" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip)"/><circle cx="865" cy="125" r="79" fill="none" stroke="{ACCENT}" stroke-width="3"/>'
    else:
        s+=f'<path d="M790 125 Q860 30 940 125 Q860 220 790 125Z" fill="none" stroke="{ACCENT}" stroke-opacity=".3" stroke-width="2"/>'
        if STATIC:
            s+=f'<circle cx="850" cy="78" r="4" fill="{ACCENT}"/><circle cx="920" cy="150" r="3" fill="#fff"/>'
        else:
            s+=f'<g class="motion-only"><circle cx="850" cy="78" r="4" fill="{ACCENT}" class="twinkle"/><circle cx="920" cy="150" r="3" fill="#fff" class="twinkle"/><animate attributeName="opacity" values="0.6;1;0.6" dur="5s" repeatCount="indefinite"/></g>'
    save("hero.svg",s)

def tile(font,n,title,sub,href,delay):
    s=start(320,132,font,delay)+box(320,132,18)
    s+=f'<a href="{x(href)}"><g class="enter"><rect x="1" y="1" width="318" height="130" rx="18" fill="url(#brand)" opacity=".24"/><text x="22" y="43" fill="{ACCENT}" font-size="13">0{n} / PROFILE</text><text x="22" y="78" fill="{FG}" font-size="20" font-weight="700">{x(title)}</text><text x="22" y="105" fill="{MUTED}" font-size="11">{x(sub)}</text></g></a>'
    save(f"tile-{n}.svg",s)

def activity(days):
    lookup={date.fromisoformat(z["date"]):z["count"] for z in days}
    today=date.today(); cursor=today if lookup.get(today,0)>0 else today-timedelta(days=1); streak=0
    while lookup.get(cursor,0)>0: streak+=1; cursor-=timedelta(days=1)
    active=sum(v>0 for v in lookup.values())
    weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    totals={d:0 for d in weekdays}; months={calendar.month_abbr[m]:0 for m in range(1,13)}
    for d,v in lookup.items(): totals[weekdays[d.weekday()]]+=v; months[d.strftime("%b")]+=v
    return streak,active,max(totals,key=totals.get) if any(totals.values()) else "—",months

def chart(font,days,total):
    streak,active,busy,months=activity(days); maximum=max(months.values()) or 1
    s=start(1000,350,font,2)+box(1000,350)
    s+=f'<g class="enter"><text x="35" y="48" fill="{FG}" font-size="23" font-weight="700">Contribution pulse</text><text x="35" y="75" fill="{MUTED}" font-size="13">Monthly activity · contribution calendar</text><text x="720" y="47" fill="{ACCENT}" font-size="15">{total:,} CONTRIBUTIONS</text>'
    for xpos,val,label in [(38,str(streak),"DAY STREAK"),(350,str(active),"ACTIVE DAYS"),(665,busy.upper(),"BUSIEST DAY")]:
        s+=f'<rect x="{xpos}" y="100" width="280" height="65" rx="13" fill="#2A1C20" stroke="#55353D"/><text x="{xpos+17}" y="130" fill="{FG}" font-size="22" font-weight="700">{x(val)}</text><text x="{xpos+17}" y="151" fill="{MUTED}" font-size="10">{label}</text>'
    bw=(916-11*9)/12
    for i,(m,v) in enumerate(months.items()):
        h=max(3,v/maximum*100); xpos=42+i*(bw+9); ypos=305-h
        s+=f'<rect x="{xpos:.1f}" y="{ypos:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="5" fill="url(#brand)"/><text x="{xpos+bw/2:.1f}" y="328" fill="{MUTED}" font-size="10" text-anchor="middle">{m}</text>'
    s+="</g>"; save("contributions-monthly.svg",s)

def repo(font,repo,n):
    name,desc,stack=repo; url=f"https://github.com/{USER}?tab=repositories"
    s=start(1000,176,font,2.8+(n-1)*.45)+box(1000,176)
    s+=f'<a href="{url}"><g class="enter"><rect x="1" y="1" width="998" height="174" rx="20" fill="url(#brand)" opacity=".18"/><text x="35" y="43" fill="{ACCENT}" font-size="13">FEATURED REPOSITORY / 0{n}</text><text x="35" y="88" fill="{FG}" font-size="29" font-weight="700">{x(name)}</text><text x="36" y="119" fill="{MUTED}" font-size="15">{x(desc)}</text><text x="36" y="151" fill="{ACCENT}" font-size="12">{x(stack)}</text><text x="930" y="94" fill="{ACCENT}" font-size="27" text-anchor="middle">↗</text></g></a>'
    save(f"repo-{n}.svg",s)

def graph(font,days):
    bydate={date.fromisoformat(z["date"]):z["count"] for z in days}
    startdate=max(bydate)-timedelta(days=363) if bydate else date.today()-timedelta(days=363)
    startdate-=timedelta(days=(startdate.weekday()+1)%7); maxv=max(bydate.values()) if bydate else 1
    colors=["#2A2023","#54232D","#82303F","#B34A5D","#E08A9A"]
    s=start(1000,240,font,5)+box(1000,240)
    s+=f'<g class="enter"><text x="35" y="43" fill="{FG}" font-size="22" font-weight="700">Contribution graph</text><text x="35" y="67" fill="{MUTED}" font-size="12">A year of showing up, one square at a time</text>'
    for i in range(371):
        d=startdate+timedelta(days=i); count=bydate.get(d,0); level=0 if not count else min(4,max(1,int(count/maxv*4)+1))
        s+=f'<rect x="{35+(i//7)*17}" y="{91+(i%7)*17}" width="12" height="12" rx="3" fill="{colors[level]}"><title>{d.isoformat()}: {count} contributions</title></rect>'
    s+=f'<text x="35" y="224" fill="{MUTED}" font-size="11">{len(bydate)} days tracked</text><text x="820" y="224" fill="{ACCENT}" font-size="11">LESS ▪ ▪ ▪ ▪ MORE</text></g>'
    save("contribution-graph.svg",s)

def main():
    days,total=get_days(); font=font_data(); hero(font)
    tile(font,1,"About me","THE HUMAN BEHIND THE COMMITS",f"https://github.com/{USER}",.8)
    tile(font,2,"Projects","THINGS I'VE BUILT",f"https://github.com/{USER}?tab=repositories",1.1)
    tile(font,3,"Git-Tulkun","MY CONTRIBUTION COMPANION","https://github.com/PramudithaN/git-tulkun",1.4)
    chart(font,days,total)
    for n,r in enumerate(REPOS,1): repo(font,r,n)
    graph(font,days); print(f"Generated {len(list(OUT.glob('*.svg')))} SVG cards in {OUT}")

if __name__=="__main__": main()
