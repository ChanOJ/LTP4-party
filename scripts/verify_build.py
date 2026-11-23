#!/usr/bin/env python3
"""Verify site/ (stdlib only, read-only):  python3 scripts/verify_build.py [--build site]

Hard checks (exit 1): no macro / ASP / form leftovers; only the removal-contact `mailto:` (full-width @);
no IPv4 other than the party LAN (10.x); every page declares iso-8859-1, has the removal footer;
every internal link and image resolves (case-sensitive, like bunny.net); robots.txt allows all and
sitemap.xml lists every page; and, when the raw store is present, no login code, login nick, IP,
host name or user agent (public IPs) of the LTP database appears in any published file.
"""
import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("ID3X_RAW") or Path.home() / "Code" / "id3x" / "raw")
FOOTER = "To be removed from this page, contact me."
MAIL = "mailto:chandra_oj＠pm.me"
LINK = re.compile(r"""(?i)\b(?:href|src|background)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""")
BAD = [("macro", r"\$\$"), ("asp", r"<%|%>"), ("form", r"(?i)<form\b|<input\b|<textarea\b|<select\b"),
       ("script", r"(?i)<script\b"), ("credentials", r"(?i)logins?\b|listlogins|password"), ("ascii @", r"@")]
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(REPO / "site"))
    site = Path(ap.parse_args().build)
    errs = []
    files = {p.relative_to(site).as_posix(): p for p in sorted(site.rglob("*")) if p.is_file()}
    pages = [f for f in files if f.endswith(".html")]
    for rel in pages:
        t = files[rel].read_bytes().decode("iso-8859-1")
        if "charset=iso-8859-1" not in t:
            errs.append(f"{rel}: no iso-8859-1 charset")
        if FOOTER not in t or MAIL.encode("ascii", "xmlcharrefreplace").decode() not in t:
            errs.append(f"{rel}: removal footer missing")
        t2 = t.replace(MAIL.encode("ascii", "xmlcharrefreplace").decode(), "")
        for name, rx in BAD:
            if re.search(rx, t2):
                errs.append(f"{rel}: {name} found")
        for ip in IPV4.findall(t):
            if not ip.startswith("10."):
                errs.append(f"{rel}: non-LAN IP {ip}")
        for m in LINK.finditer(t):
            u = next(g for g in m.groups() if g is not None)
            if re.match(r"(?i)(https?:|mailto:|#)", u):
                continue
            path = unquote(urlsplit(u).path)
            tgt = (path.lstrip("/") or "index.html") if path.startswith("/") else (Path(rel).parent / path).as_posix()
            if tgt not in files:
                errs.append(f"{rel}: broken link {u}")
        if "@" in t.replace("&#65312;", ""):
            errs.append(f"{rel}: e-mail-like text")
    for name in ("robots.txt", "sitemap.xml"):
        if name not in files:
            errs.append(f"{name} missing")
    if "robots.txt" in files:
        r = files["robots.txt"].read_text()
        if "Disallow: /" in r or "Allow: /" not in r:
            errs.append("robots.txt must allow everything")
    if "sitemap.xml" in files:
        s = files["sitemap.xml"].read_text()
        for rel in pages:
            if f"/{'' if rel == 'index.html' else rel}</loc>" not in s:
                errs.append(f"sitemap.xml lacks {rel}")
    db = RAW / "db" / "LTP.sqlite"
    if db.is_file():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        blob = "\n".join(files[r].read_bytes().decode("iso-8859-1") for r in pages)
        words = set(re.findall(r"[A-Za-z0-9_]+", blob))
        for (code,) in con.execute("SELECT code FROM LOGINS"):
            if code.strip() in words and len(code.strip()) == 5 and not re.fullmatch(r"[a-z]+", code.strip()):
                errs.append(f"login code in the site: {code}")
        for (v,) in con.execute("SELECT DISTINCT ip FROM ONELINER WHERE ip IS NOT NULL UNION SELECT DISTINCT hostname FROM ONELINER WHERE hostname<>'' UNION SELECT DISTINCT user_agent FROM ONELINER WHERE user_agent IS NOT NULL"):
            if v.strip() and not v.strip().startswith("10.") and v.strip() in blob:
                errs.append(f"private visitor value in the site: {v[:30]}")
    else:
        print("(raw store absent: private-data checks skipped)")
    if errs:
        print("\n".join(errs))
        return 1
    print(f"{len(pages)} pages, {len(files)} files: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
