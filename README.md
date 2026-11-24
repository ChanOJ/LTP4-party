# LTP4-party

**Lucky & Tigroo Party 4, the intranet of the party (25-27 August 2000).** LTP was a French
demoparty series organised by Orange Juice. This is the website that ran on the LAN of the party
(`www.ltp.net`) while LTP4 was happening: news, oneliner, schedule, infos, the Fast Code rules and
the vote ranking. It was served by id3, the in-house ASP engine of Orange Juice (skin `ltp_party`)
over a small SQL Server database. The public information site of LTP4 is a separate archive
([LTP4](../LTP4), [LTP4-postparty](../LTP4-postparty)).

Published as a **100 % static, read-only site** on bunny.net at the hostname of
[`site.json`](site.json) (`ltp4-party.sauthier.family`). Visitors can never write anything: the
pages are rendered once from the data, the CDN only serves files, and every method except
GET/HEAD/OPTIONS is refused at the edge.

## What the database held (`LTP_Data.MDF`, 2006-07-24 copy)

LTP4 data only: 18 news (15 active), 271 oneliner lines (2000-08-22 to 2000-09-28), 31 schedule
entries, 15 compos, 181 entries with their final place, 4,998 vote rows from 310 voters, 804
login codes (printed on the party passcards), 12 jury assignments.

## Pages

| Page | Content | From |
| --- | --- | --- |
| `index.html` | News + the last 20 oneliner lines (as the original home page) | `NEWS` (active only), `ONELINER` |
| `oneliner.html` | The whole oneliner of the party | `ONELINER` |
| `schedule.html` | Time table (deadlines and compos) | `SCHEDULE`, `COMPOS` |
| `results.html` | Final ranking of every compo (was `votes.htm`) | `PRODS`, `COMPOS`, counts of `VOTES` |
| `infos.html`, `fastcode.html` | Bar prices, network settings; Fast Code rules | skin templates |

Same layout and pictures as the original skin. Schedule colours show the plan, not the "passed"
state of the original (it greyed out events as time went by).

## Removed or not published

- Forms: add news, add vote, upload / submit / delete a prod, login and logout, edit the schedule,
  the backoffice and `listlogins.txt`. The entry files (`/zi/<compo>/*.zip`) are not archived.
- Never published: login codes and nicks (`LOGINS`), who voted for what (`VOTES` rows), jury
  assignments, visitors' IPs, host names and user agents of the oneliner, inactive news (one holds
  a private e-mail address), the `$$MACRO$$` templates and the engine. The party's LAN addresses
  (`10.0.x.x`) are published as written.
- Oneliner: only 2000-08-25 to 2000-08-27 (before, the author was testing the script), otherwise
  complete and unfiltered (old, anonymous lines).
- News links to `ltp.ojuice.net` point to the LTP4 archive; links to dead targets (a LAN FTP
  address, an e-mail address, `upload.htm`) are plain text. The fast code link to `check.zip` on
  `ojuice.net` (dead, no new address known) keeps its original address.
- Pages that list people (index, oneliner, results, fastcode) end with "To be removed from this
  page, contact me."; schedule and infos list no person and have no such footer.

## Layout

| Path | Content |
| --- | --- |
| `site/` | Generated static site, exactly as served (committed: 23 small files) |
| `hosting/404.html` | Custom 404 page, deployed next to `site/` |
| `site.json` | Hosting settings: repository, storage zone, pull zone, hostname, 404 page |
| `scripts/statify.py` | Raw store -> `site/` (deterministic) |
| `scripts/verify_build.py` | Checks `site/`: no macro, form or credential; links resolve; footer, robots, sitemap; no private value of the database |
| `scripts/check_excludes.py`, `scripts/exclude-globs.txt` | Fails if `site/` holds a forbidden path |
| `scripts/preview.py` | Local preview with the charsets of the edge rules |
| `scripts/deploy.py`, `scripts/smoke_test.py`, `scripts/bunny.py`, `scripts/bootstrap.sh`, `infra/` | Hosting (OpenTofu, state encrypted) |

DNS is not managed here: the hostname is a CNAME to `ltp4-party.b-cdn.net` at Infomaniak.

## Regenerating `site/`

Inputs come from the shared raw store `~/Code/id3x/raw` (or `$ID3X_RAW`): skin
`id3/z/ltp_party`, database `db/LTP.sqlite` (extracted from `Data/LTP_Data.MDF` with
`scripts/mdf/extract_sqlite.py` of OrangeJuiceV3). It holds login codes and IPs: never copy it here.

```bash
python3 -I scripts/statify.py
```

```bash
python3 -I scripts/verify_build.py
```

```bash
python3 scripts/check_excludes.py
```

```bash
python3 scripts/preview.py 3733
```
