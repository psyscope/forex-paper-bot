"""Daily paper run for the forex paper bot (run by GitHub Actions on weekdays). Paper only: no broker, no orders.
1. Fetch the ECB 90-day euro reference rates XML directly.
2. Sanity-check the values and add only dates newer than the newest row already in ecb_rates.csv / g10_rates.csv
   (existing rows are never changed).
3. Run sim.py (breakout line) and carry.py (carry line).
4. Add one row to the table in log.md and update status.json (consecutive data failures).
Test window: runs 2026-11-23 to 2026-12-18; outside it, exits without changes unless FORCE_RUN=1.
policy_rates.csv is not refreshed here (no reliable free source a script can check); it is kept as set and edited by hand."""
import csv, datetime as dt, json, os, subprocess, sys, urllib.request, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
G10 = ["USD", "JPY", "GBP", "CHF", "AUD", "NZD", "CAD", "SEK", "NOK"]
RANGES = {"USD": (0.9, 1.4), "JPY": (120, 230), "GBP": (0.7, 1.0), "CHF": (0.8, 1.1), "AUD": (1.3, 2.0),
          "NZD": (1.5, 2.3), "CAD": (1.3, 1.8), "SEK": (9, 13.5), "NOK": (9, 13.5)}
FIRST, LAST = "2026-11-23", "2026-12-18"
P = lambda f: os.path.join(HERE, f)

def read_rows(f):
    with open(P(f)) as fh: r = csv.reader(fh); head = next(r); return head, [row for row in r if row]

def write_rows(f, head, rows):
    with open(P(f), "w", newline="") as fh: w = csv.writer(fh, lineterminator="\n"); w.writerow(head); w.writerows(rows)

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "forex-paper-bot (paper trading simulation)"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=60).read())
    out = {}
    for c in root.iter():
        if c.tag.endswith("Cube") and "time" in c.attrib:
            out[c.attrib["time"]] = {k.attrib["currency"]: k.attrib["rate"] for k in c if "currency" in k.attrib}
    return out

def main():
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if not (FIRST <= today <= LAST) and os.environ.get("FORCE_RUN") != "1":
        print(f"{today} is outside the test window {FIRST}..{LAST}; nothing to do."); return
    status = json.load(open(P("status.json"))) if os.path.exists(P("status.json")) else {"consecutive_failures": 0}
    prev = json.load(open(P("state.json"))); prev_c = json.load(open(P("carry_state.json")))
    note, added = [], []
    try:
        data = fetch()
        eh, er = read_rows("ecb_rates.csv"); gh, gr = read_rows("g10_rates.csv")
        last_e, last_g = max(r[0] for r in er), max(r[0] for r in gr)
        good = {}
        for d, rates in data.items():
            if all(c in rates and RANGES[c][0] <= float(rates[c]) <= RANGES[c][1] for c in G10): good[d] = rates
            elif d > last_e: note.append(f"skipped {d}: missing or out-of-range rate")
        if not good: raise ValueError("no valid rows in ECB file")
        new_e = sorted((d for d in good if d > last_e), reverse=True)
        new_g = sorted((d for d in good if d > last_g), reverse=True)
        write_rows("ecb_rates.csv", eh, [[d] + [good[d][c] for c in eh[1:]] for d in new_e] + er)
        write_rows("g10_rates.csv", gh, [[d] + [good[d][c] for c in gh[1:]] for d in new_g] + gr)
        added = new_e
        status["consecutive_failures"] = 0
        if not added: note.append("no new data")
    except Exception as e:  # keep the run going on old data, but count the failure
        status["consecutive_failures"] += 1
        note.append(f"data problem: {type(e).__name__}: {e}"[:160])
    status["last_run"] = today
    for s in ("sim.py", "carry.py"):
        subprocess.run([sys.executable, "-I", P(s)], check=True, stdout=subprocess.DEVNULL)
    st, cs = json.load(open(P("state.json"))), json.load(open(P("carry_state.json")))
    for t in st["trades"][len(prev["trades"]):]:
        note.append(f"exit {t['pair']} {'long' if t['side'] == 1 else 'short'} ({t['reason']}) P&L {t['pnl']:+.2f}")
    for pair, o in st["open_positions"].items():
        if pair not in prev["open_positions"] or prev["open_positions"][pair]["entry_date"] != o["entry_date"]:
            note.append(f"new {pair} {'long' if o['side'] == 1 else 'short'} at {o['entry']} ({o['entry_date']})")
    for r in cs["rebalances"][len(prev_c["rebalances"]):]:
        note.append(f"carry rebalance {r['date']}: {r['to'][0]}/{r['to'][1]}")
    if added: note.insert(0, f"added {', '.join(sorted(added))}")
    if os.environ.get("FORCE_RUN") == "1": note.insert(0, "manual run")
    if today >= LAST: note.append("FINAL RUN")
    opens = "; ".join(f"{p} {'long' if o['side'] == 1 else 'short'} {o['entry']}" for p, o in st["open_positions"].items()) or "none"
    row = (f"| {today} | {st['last_data_date']} | {st['equity']:.2f} | {st['return_pct']:+.2f}% | {cs['equity']:.2f} | "
           f"{cs['return_pct']:+.2f}% | {opens} | {st['closed_trades']} | {'; '.join(note) or '-'} |")
    with open(P("log.md"), "a") as fh: fh.write(row + "\n")
    json.dump(status, open(P("status.json"), "w"), indent=1)
    print(row)

if __name__ == "__main__":
    main()
