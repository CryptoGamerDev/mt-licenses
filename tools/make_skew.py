# -*- coding: utf-8 -*-
# Generator sygnalu SKEW ze ZRODLA OFICJALNEGO (CBOE) - wersja do automatu GitHub Actions.
#   sygnal(D+1) = 1.0 gdy SKEW(D) > SMA200 z okna [D-200, D-1], inaczej 0.0
# Brak zaleznosci poza biblioteka standardowa - dziala na czystym runnerze.
import urllib.request, ssl, datetime as dt, sys, os

URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv"
WIN = 200
OUT = sys.argv[1] if len(sys.argv) > 1 else "xag_skew.csv"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
txt = urllib.request.urlopen(req, timeout=90, context=ssl.create_default_context()).read().decode("utf-8", "replace")

rows = []
for line in txt.strip().splitlines():
    p = line.split(",")
    if len(p) < 2 or p[0].upper().startswith("DATE"):
        continue
    try:
        d = dt.datetime.strptime(p[0].strip(), "%m/%d/%Y").date()
        v = float(p[1])
    except Exception:
        continue
    if v > 0:
        rows.append((d, v))
rows.sort()
if len(rows) < 1000:
    sys.exit("BLAD: za malo danych z CBOE (%d)" % len(rows))

dates = [r[0] for r in rows]
vals = [r[1] for r in rows]
out = []
run = sum(vals[:WIN])
for i in range(WIN, len(vals)):
    sma = run / WIN                                   # okno [i-WIN, i-1], BEZ dnia biezacego
    out.append((dates[i] + dt.timedelta(days=1), 1.0 if vals[i] > sma else 0.0))
    run += vals[i] - vals[i - WIN]

body = "".join("%s;%.1f\n" % (d.strftime("%Y.%m.%d"), v) for d, v in out)
old = ""
if os.path.exists(OUT):
    old = open(OUT, encoding="ascii", errors="replace").read()
with open(OUT, "w", encoding="ascii", newline="\n") as f:
    f.write(body)

on = sum(v for _, v in out) / len(out)
print("SKEW z CBOE: %d notowan, %s .. %s" % (len(vals), dates[0], dates[-1]))
print("zapisano %s: %d rekordow, %s .. %s" % (OUT, len(out), out[0][0], out[-1][0]))
print("filtr wlaczony %.1f%% czasu" % (100 * on))
print("ZMIANA" if body != old else "bez zmian")
