#!/usr/bin/env python3
"""rate-split.py — why did a rate move? Splits a change in money per 1,000 views into mix (which posts got the views)
and rate (what each kind of post earns), from any CSV export.

  rate-split.py <export.csv> --date <col> --split YYYY-MM-DD --money <col> --views <col>
             [--group <col>] [--bucket 'name=regex' ...] [--top 12]
  rate-split.py --selftest

Rows dated before --split are "before", the rest "after". Groups are the values of --group (a post, a country, a
format), or, with --bucket, named regexes matched against --group: --bucket 'obituary=dies|dead|passed-away'. Rows no
bucket matches go to "other".

The answer it prints, in plain words: the rate went from X to Y; Z of that came from the mix shifting, the rest from
the rates themselves. A falling rate with a mix cause means "different posts got the views", not "we are paid less".
"""
from __future__ import annotations
import argparse, csv, re, sys
from collections import defaultdict


def num(v: str) -> float:
    v = (v or "").strip().replace(",", "").replace("$", "").replace("%", "")
    try: return float(v) if v else 0.0
    except ValueError: return 0.0


def split(rows, *, date, cut, money, views, label):
    """→ {window: {group: [money, views]}} for windows 'before' and 'after'."""
    acc = {"before": defaultdict(lambda: [0.0, 0.0]), "after": defaultdict(lambda: [0.0, 0.0])}
    for r in rows:
        d = (r.get(date) or "").strip()[:10]
        if not d: continue
        g = acc["before" if d < cut else "after"][label(r)]
        g[0] += num(r.get(money, "")); g[1] += num(r.get(views, ""))
    return acc


def decompose(acc):
    """Total rate a 1,000 views in each window, and the change split into mix and rate parts."""
    tot = {w: [sum(g[0] for g in acc[w].values()), sum(g[1] for g in acc[w].values())] for w in acc}
    rate = lambda m, v: 1000 * m / v if v else 0.0
    R0, R1 = rate(*tot["before"]), rate(*tot["after"])
    mix = 0.0
    for g in set(acc["before"]) | set(acc["after"]):
        m0, v0 = acc["before"].get(g, [0.0, 0.0]); m1, v1 = acc["after"].get(g, [0.0, 0.0])
        s0 = v0 / tot["before"][1] if tot["before"][1] else 0; s1 = v1 / tot["after"][1] if tot["after"][1] else 0
        ref = rate(m0, v0) if v0 else rate(m1, v1)
        mix += (s1 - s0) * ref
    return tot, R0, R1, mix, (R1 - R0) - mix


def selftest() -> int:
    rows = ([{"d": "2026-01-01", "p": "story-a", "usd": "16", "pv": "1000"}, {"d": "2026-01-01", "p": "obit-a", "usd": "1", "pv": "200"}]
            + [{"d": "2026-01-09", "p": "story-a", "usd": "4", "pv": "250"}, {"d": "2026-01-09", "p": "obit-b", "usd": "5", "pv": "1000"}])
    lab = lambda r: "obit" if re.search("obit", r["p"]) else "other"
    acc = split(rows, date="d", cut="2026-01-05", money="usd", views="pv", label=lab)
    tot, R0, R1, mix, rate = decompose(acc)
    checks = {
        "windows split by date": tot["before"] == [17.0, 1200.0] and tot["after"] == [9.0, 1250.0],
        "rates": round(R0, 2) == 14.17 and round(R1, 2) == 7.2,
        "mix explains most of a drop caused by mix": mix < 0 and abs(mix) > abs(rate),
        "parts add up": abs((mix + rate) - (R1 - R0)) < 1e-9,
        "money text parses": num("$1,234.50") == 1234.5 and num("") == 0.0,
    }
    for n, ok in checks.items(): print(f"{'ok  ' if ok else 'FAIL'} {n}")
    return 0 if all(checks.values()) else 1


def main() -> int:
    if sys.argv[1:] == ["--selftest"]: return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv"); ap.add_argument("--date", required=True); ap.add_argument("--split", required=True)
    ap.add_argument("--money", required=True); ap.add_argument("--views", required=True)
    ap.add_argument("--group"); ap.add_argument("--bucket", action="append", default=[]); ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.split): sys.exit("rate-split: --split wants YYYY-MM-DD")
    buckets = []
    for b in a.bucket:
        name, _, rx = b.partition("=")
        if not name or not rx: sys.exit(f"rate-split: --bucket wants name=regex, got {b!r}")
        try: buckets.append((name, re.compile(rx, re.I)))
        except re.error as e: sys.exit(f"rate-split: --bucket {name}: bad regex: {e}")
    if buckets and not a.group: sys.exit("rate-split: --bucket needs --group, the column the regexes read")
    def label(r):
        v = (r.get(a.group) or "").strip() if a.group else "all"
        if not buckets: return v
        return next((n for n, rx in buckets if rx.search(v)), "other")
    try:
        with open(a.csv, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [c for c in (a.date, a.money, a.views, a.group) if c and c not in (reader.fieldnames or [])]
            if missing: sys.exit(f"rate-split: no column {missing} in {a.csv}; columns are {reader.fieldnames}")
            acc = split(reader, date=a.date, cut=a.split, money=a.money, views=a.views, label=label)
    except OSError as e: sys.exit(f"rate-split: {e}")
    tot, R0, R1, mix, rate = decompose(acc)
    if not tot["before"][1] or not tot["after"][1]: sys.exit("rate-split: one window has no views; check --split and --date")
    groups = sorted(set(acc["before"]) | set(acc["after"]), key=lambda g: -(acc["after"].get(g, [0, 0])[1] + acc["before"].get(g, [0, 0])[1]))
    print(f"{'group':40} {'views before':>12} {'share':>6} {'$/1k':>6}   {'views after':>11} {'share':>6} {'$/1k':>6}")
    for g in groups[: a.top]:
        row = []
        for w in ("before", "after"):
            m, v = acc[w].get(g, [0.0, 0.0]); row += [f"{int(v):>12,}" if w == "before" else f"{int(v):>11,}", f"{v / tot[w][1]:>6.0%}", f"{1000 * m / v if v else 0:>6.1f}"]
        print(f"{g[:40]:40} {row[0]} {row[1]} {row[2]}   {row[3]} {row[4]} {row[5]}")
    if len(groups) > a.top: print(f"... and {len(groups) - a.top} more groups")
    print(f"\nall: ${tot['before'][0]:,.0f} on {int(tot['before'][1]):,} views = {R0:.2f} a 1,000 before;"
          f" ${tot['after'][0]:,.0f} on {int(tot['after'][1]):,} = {R1:.2f} after ({R1 - R0:+.2f}).")
    print(f"of that change: {mix:+.2f} from the mix (which groups got the views), {rate:+.2f} from the groups' own rates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
