# LTP4-party: context for Claude sessions

Static archive of the LTP4 party intranet (www.ltp.net, 2000-08-25..27, id3 skin `ltp_party`).
Same family and hosting as `~/Code/LTP3-party`; context of id3 sites: `~/Code/id3x/CLAUDE.md`.

- Inputs only from `~/Code/id3x/raw` (skin `id3/z/ltp_party`, `db/LTP.sqlite`). The database holds
  login codes, who voted what, IPs: never copy any of it into the repository or a page.
- `site/` is small and committed; regenerate with `python3 -I scripts/statify.py`, build twice,
  same hashes; then `scripts/verify_build.py` and `scripts/check_excludes.py`.
- Pages listing people keep the footer "To be removed from this page, contact me." (statify `page()`).
