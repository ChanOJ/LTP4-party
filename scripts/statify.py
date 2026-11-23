#!/usr/bin/env python3
"""Render the LTP4 party intranet (www.ltp.net, 2000-08-25..27) into plain static HTML.

    python3 -I scripts/statify.py            # raw store ~/Code/id3x/raw (or $ID3X_RAW) -> site/

Inputs (read only, never published as such): the id3 skin `id3/z/ltp_party` (pictures) and the
SQLite extraction `db/LTP.sqlite` of the LTP database (tables NEWS, ONELINER, SCHEDULE, COMPOS,
PRODS, VOTES). The `$$MACRO$$` templates are not interpreted: the five public pages are written
here with the same layout, from the data. Deterministic: same inputs, same bytes.

Not published: login codes (LOGINS, JURY), who voted for what (VOTES rows), IPs, host names and
user agents (ONELINER), inactive news, upload / vote / edit forms, backoffice, listlogins.txt.
"""
from __future__ import annotations

import html
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("ID3X_RAW") or Path.home() / "Code" / "id3x" / "raw")
SKIN = RAW / "id3" / "z" / "ltp_party"
DB = RAW / "db" / "LTP.sqlite"
SITE = REPO / "site"
HOST = "ltp4-party.sauthier.family"
LTP4_HOST = "ltp4.sauthier.family"  # the public LTP4 information site (ltp.ojuice.net)
ENC = "iso-8859-1"
MAIL = "chandra_oj＠pm.me"  # full-width @ on purpose (anti-scraping), as on the other archives

# Pictures referenced by the pages (lower-cased names: bunny.net is case-sensitive).
PICTURES = ["top.jpg", "Anim_logo.gif", "menu-bkg.gif", "news-off.gif", "arrow-off.gif", "charts-off.gif",
            "schedule-off.gif", "infos-off.gif", "small-oj.gif", "adjust.gif", "small-news.gif",
            "small-votes.gif", "small-schedule.gif", "small-infos.gif", "ojtv0.gif"]

# Oneliner: only the party itself (from 2000-08-25: before, the author was testing the script; after
# 2000-08-28 one more test line). Lines naming a person with an accusation or an insult, and the line
# publishing a visitor's LAN IP address, are left out (same rule as the people sheets of the other archives).
ONELINER_FROM, ONELINER_TO = "2000-08-25", "2000-08-28"
ONELINER_DROP = re.compile(r"(?i)\bis gay\b|netbus|nb attack|\bis stink\b|can i fuk|\bgo to shower\b|10\.0\.1\.\d+")
# The intranet's own links: old address -> page of this archive (None = no link, the target is gone).
LINKS = {
    "http://www.ltp.net/schedule.htm": "/schedule.html",
    "http://www.ltp.net/infos.htm": "/infos.html",
    "http://www.ltp.net/fastcode.htm": "/fastcode.html",
    "http://www.ltp.net/votes.htm": "/results.html",
    "http://www.ltp.net/upload.htm": None,
    "http://ltp.ojuice.net/": f"https://{LTP4_HOST}/",
    "http://www.ojuice.net/": "https://orangejuicev3.sauthier.family/",
}


def esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def link_target(url: str | None) -> str | None:
    if not url:
        return None
    return LINKS.get(url)  # anything else (mailto:, a LAN IP, ...) is not a usable link any more


def day_name(dt: datetime, short: bool) -> str:
    n = dt.strftime("%A")
    return n[:3] if short else n


def parse(dt: str) -> datetime:
    return datetime.strptime(dt[:19], "%Y-%m-%d %H:%M:%S")


CSS = """<STYLE type="text/css">
A:link, A:visited, A:active, A:hover {color:#FF9600}
A.txt:link, A.txt:visited {color:#AAAAAA}
A.txt:hover {color:#FFFFFF}
TD {font-family:Verdana,'DejaVu Sans',Geneva,sans-serif;font-size:10pt}
TABLE.specialtable {background-color:#404040}
.normal {font-family:Verdana,'DejaVu Sans',Geneva,sans-serif;font-size:10pt}
.aslink {color:#FF9600}
.title2 {font-size:12pt;font-weight:bold;color:#FF9600}
.title6 {font-size:24pt;font-weight:bold;color:#FF9600}
.date {font-size:7.5pt;color:#FF9600}
.smtxt {font-size:7.5pt}
.menutop {font-size:7.5pt}
.menubottom {font-size:8pt}
.note {font-size:8pt;color:#808080}
</STYLE>"""

MENU = [("/", "news-off.gif", "news"), ("/results.html", "charts-off.gif", "votes"),
        ("/schedule.html", "schedule-off.gif", "schedule"), ("/infos.html", "infos-off.gif", "infos")]
SMALL = [("/", "small-news.gif", "news"), ("/results.html", "small-votes.gif", "votes"),
         ("/schedule.html", "small-schedule.gif", "schedule"), ("/infos.html", "small-infos.gif", "infos")]


def page(title: str, body: str) -> str:
    menu = "".join(f'\t\t\t<A href="{u}"><IMG src="/pictures/{i}" alt={a} border=0>'
                   f'<IMG src="/pictures/arrow-off.gif" border=0></A><BR><BR>\n' for u, i, a in MENU)
    small = " | ".join(f'<A href="{u}"><IMG alt={a} border=0 src="/pictures/{i}"></A>' for u, i, a in SMALL)
    return f"""<HTML>
<HEAD>
<META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<META name="DESCRIPTION" content="Lucky and Tigroo Party 4: the intranet of the party (archive)">
<META name="ROBOTS" content="ALL">
<TITLE>{esc(title)}</TITLE>
{CSS}
</HEAD>

<BODY bgcolor="#4C4A47" text="#AAAAAA" link="#FF9600" vlink="#FF9600" alink="#FFBB00" topmargin=0 leftmargin=0 marginwidth=0 marginheight=0>

<TABLE border="0" cellpadding="0" cellspacing="0" width="780">
	<TR>
		<TD colspan=2>
			<TABLE border="0" cellpadding="0" cellspacing="0" width="780">
				<TR>
					<TD width=640 height=141 rowspan=2><IMG src="/pictures/top.jpg" alt="Lucky and Tigroo Party 4"></TD>
					<TD width=240 valign="top" height=41><IMG src="/pictures/anim_logo.gif" alt=""></TD>
				</TR>
				<TR>
					<TD width=240 valign="middle" height=100 align="center"><FONT class=smtxt>
						LTP4 party intranet<BR>(www.ltp.net)<BR>25-27 August 2000<BR><BR>
						Archive: read-only</FONT></TD>
				</TR>
			</TABLE>
		</TD>
	</TR>
	<TR>
		<TD width="125" rowspan=2 valign="top" background="/pictures/menu-bkg.gif">
{menu}			<IMG src="/pictures/small-oj.gif" border=0 alt=""><BR><IMG src="/pictures/adjust.gif" width=125 height=1 alt="">
		</TD>
		<TD width="655" valign="top">
{body}
		</TD>
	</TR>
	<TR>
		<TD width="655" valign="bottom"><FONT class=menubottom><BR><BR>[ {small} ]<BR>
<A href="/oneliner.html">oneliner</A> | <A href="/fastcode.html">fast code</A> | <A href="https://{LTP4_HOST}/">LTP4 information site</A>
<HR size="1" align="left">
<FONT class=note>Archive of the intranet that ran on the LAN of the party. Nothing can be sent from this site.<BR>
<A href="mailto:{MAIL}">To be removed from this page, contact me.</A></FONT>
</FONT></TD>
	</TR>
</TABLE>
</BODY>
</HTML>
"""


def render_news(con) -> str:
    rows = con.execute("SELECT idnews, dt, title, link, news FROM NEWS WHERE isactive=1 ORDER BY dt DESC, idnews DESC").fetchall()
    out = []
    for _, dt, title, link, news in rows:
        d = parse(dt)
        t = esc(title)
        target = link_target(link)
        if target:
            t = f'<A href="{target}">{t}</A>'
        out.append(f'\t\t\t<FONT class=title2>{t}</FONT> <FONT class=date>[{day_name(d, True)}, {d:%H}h{d:%M}]<BR>\n'
                   f'\t\t\t</FONT> {esc(news).replace(chr(10), "<BR>")} <BR>\n\t\t\t<BR>\n')
    return "".join(out)


def oneliner_rows(con) -> list[tuple[str, str]]:
    rows = con.execute("SELECT dt, sentence FROM ONELINER WHERE dt>=? AND dt<? ORDER BY dt, id", (ONELINER_FROM, ONELINER_TO)).fetchall()
    codes = {c.strip().lower() for (c,) in con.execute("SELECT code FROM LOGINS")}  # a visitor pasted a login code once
    def has_code(s): return any(w.lower() in codes for w in re.findall(r"[A-Za-z0-9]{5}", s))
    return [(dt, s.strip()) for dt, s in rows if s.strip() and not ONELINER_DROP.search(s) and not has_code(s)]


def oneliner_html(rows, n=None) -> str:
    if n:
        rows = rows[-n:]
    return "".join(f'<FONT class=aslink>{parse(dt):%H:%M}</FONT> {esc(s)}<BR>\n' for dt, s in rows)


def render_index(con) -> str:
    rows = oneliner_rows(con)
    body = f"""<TABLE border="0" cellpadding="0" cellspacing="0" width="100%">
	<TR>
		<TD valign="top"><FONT class=title6>News</FONT><BR><BR>
<FONT class=normal>
{render_news(con)}</FONT></TD>
		<TD width="20">&nbsp;</TD>
		<TD valign="top" width="200">
			<TABLE width="100%" cellpadding=2 class=specialtable>
				<TR>
					<TD class=smtxt>
{oneliner_html(rows, 20)}<BR>
<A href="/oneliner.html">all {len(rows)} lines of the oneliner</A>
					</TD>
				</TR>
			</TABLE>
			<BR>
			<CENTER><TABLE align="center" width=180 height=276 background="/pictures/ojtv0.gif"><TR><TD></TD></TR></TABLE></CENTER>
		</TD>
	</TR>
</TABLE>"""
    return page("Lucky and Tigroo Party 4", body)


def render_oneliner(con) -> str:
    rows = oneliner_rows(con)
    body = f"""<FONT class=title6>Oneliner</FONT><BR><BR>
<FONT class=note>Everything written on the oneliner during the party (25-27 August 2000), oldest first: {len(rows)} lines.
Times are those of the party. A few lines are left out (they name a person).</FONT><BR><BR>
<TABLE width="100%" cellpadding=4 class=specialtable><TR><TD class=smtxt>
{oneliner_html(rows)}</TD></TR></TABLE>"""
    return page("LTP4 - Oneliner", body)


def render_schedule(con) -> str:
    rows = con.execute("""SELECT a.dt, a.eventtype, a.description, a.color, b.componame FROM SCHEDULE a
                          LEFT JOIN COMPOS b ON a.idcompo=b.idcompo ORDER BY a.dt, a.idschedule""").fetchall()
    out, prev_dt, prev_day = [], None, None
    for dt, typ, desc, color, compo in rows:
        d = parse(dt)
        day = f"{day_name(d, False)} {d:%d}," if d.date() != prev_day else ""
        hour = f"{d:%H}:{d:%M}" if dt != prev_dt else ""
        prev_dt, prev_day = dt, d.date()
        label = {1: "Deadline - ", 2: "Compo - "}.get(typ, "")
        out.append(f'\t<TR>\n\t\t<TD align=right>{day} {hour}</TD>\n\t\t<TD>&nbsp;&nbsp;</TD>\n'
                   f'\t\t<TD><FONT color="{esc(color)}">{label}{esc(desc)}{esc(compo)}</FONT></TD>\n\t</TR>\n')
    body = f"""<CENTER>
<FONT class=title6>Schedule</FONT><BR>
<FONT class=note>The time table as it stood at the end of the party (deadlines in pink, compos in blue).</FONT><BR><BR>
<TABLE border=0>
{''.join(out)}</TABLE>
</CENTER>"""
    return page("LTP4 - Schedule", body)


def render_results(con) -> str:
    votes, voters = con.execute("SELECT count(*), count(DISTINCT code) FROM VOTES").fetchone()
    parts = []
    for idc, name in con.execute("SELECT idcompo, componame FROM COMPOS ORDER BY componame, idcompo"):
        prods = con.execute("""SELECT name, authors, place FROM PRODS WHERE idcompo=? ORDER BY
                               CASE WHEN place>0 THEN 0 ELSE 1 END, place, name, idproduction""", (idc,)).fetchall()
        if not prods:
            continue
        lines = []
        for pname, authors, place in prods:
            rank = f"{place}. " if place and place > 0 else "&nbsp;&nbsp;&nbsp;"
            lines.append(f"{rank}{esc(pname.strip())} by {esc(authors.strip())}<BR>\n")
        parts.append(f"<FONT class=title2>{esc(name)}</FONT><BR>\n{''.join(lines)}<BR>\n")
    body = f"""<FONT class=title6>Votes</FONT><BR><BR>
<FONT class=note>Final ranking of every compo, as recorded in the database of the party ({voters} voters, {votes} ranked
choices). Entries without a number were not ranked. The entry files and the vote form are not archived.</FONT><BR><BR>
<FONT class=normal>
{''.join(parts)}</FONT>"""
    return page("LTP4 - Votes", body)


def render_infos() -> str:
    src = (SKIN / "infos.htm").read_text(encoding="cp1252")
    src = src.replace("$$INCL:top.inc$$", "").replace("$$INCL:bottom.inc$$", "")
    for old, new in [("http://www.ltp.net/", "/"), ("http://www.ojuice.net/", "https://orangejuicev3.sauthier.family/"),
                     ("http://ltp.ojuice.net/", f"https://{LTP4_HOST}/")]:
        src = src.replace(f'href="{old}"', f'href="{new}"')
    src = src.replace(">http://www.ltp.net/<", ">http://www.ltp.net/ (this site)<").replace(">http://www.ojuice.net/<", ">www.ojuice.net<").replace(">http://ltp.ojuice.net/<", ">ltp.ojuice.net<")
    return page("LTP4 - Infos", src.strip())


def render_fastcode() -> str:
    src = (SKIN / "fastcode.htm").read_text(encoding="cp1252")
    src = src.replace("$$INCL:top.inc$$", "").replace("$$INCL:bottom.inc$$", "")
    # the original check.c was downloaded from www.ojuice.net/archives: not archived
    src = re.sub(r'<A href="http://www\.ojuice\.net/archives/check\.zip">(.*?)</a>', r"\1", src, flags=re.S | re.I)
    return page("LTP4 - Fast Code", src.strip())


def write(rel: str, text: str) -> None:
    p = SITE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode(ENC, errors="xmlcharrefreplace"))


def main() -> int:
    if not DB.is_file() or not SKIN.is_dir():
        sys.exit(f"missing input under {RAW}: {DB} / {SKIN}")
    if SITE.exists():
        shutil.rmtree(SITE)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    pages = {"index.html": render_index(con), "oneliner.html": render_oneliner(con),
             "schedule.html": render_schedule(con), "results.html": render_results(con),
             "infos.html": render_infos(), "fastcode.html": render_fastcode()}
    for rel, text in pages.items():
        write(rel, text)
    for name in PICTURES:
        dst = SITE / "pictures" / name.lower()
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKIN / "pictures" / name, dst)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: https://{HOST}/sitemap.xml\n")
    urls = "".join(f"  <url><loc>https://{HOST}/{'' if r == 'index.html' else r}</loc></url>\n" for r in sorted(pages))
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    print(f"{len(pages)} pages, {len(PICTURES)} pictures -> {SITE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
