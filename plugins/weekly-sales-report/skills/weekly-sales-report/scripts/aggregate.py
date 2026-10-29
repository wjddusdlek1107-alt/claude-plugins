"""주간 매출 집계. CSV 열: 날짜(MM-DD),주문번호,판매채널,카테고리,상품명,수량,결제금액"""
import argparse, collections, csv, sys

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("csv")
ap.add_argument("--cur", required=True, help="MM-DD:MM-DD")
ap.add_argument("--prev", required=True, help="MM-DD:MM-DD")
a = ap.parse_args()

rows = [r for r in csv.reader(open(a.csv, encoding="utf-8")) if r]


def pick(span):
    lo, hi = span.split(":")
    return [r for r in rows if lo <= r[0] <= hi]


cur, prev = pick(a.cur), pick(a.prev)
won = lambda n: f"{n:,}원"
pct = lambda c, p: f"{(c / p - 1) * 100:+.1f}%" if p else "신규"


def kpi(rs):
    s = sum(int(r[6]) for r in rs)
    o = len({r[1] for r in rs})
    return dict(sales=s, lines=len(rs), orders=o, qty=sum(int(r[5]) for r in rs), aov=round(s / o) if o else 0)


def by(rs, i):
    amt, qty, n = collections.Counter(), collections.Counter(), collections.Counter()
    for r in rs:
        amt[r[i]] += int(r[6]); qty[r[i]] += int(r[5]); n[r[i]] += 1
    return amt, qty, n


c, p = kpi(cur), kpi(prev)
print("## 핵심 지표")
print(f"총매출 | {won(c['sales'])} | {won(p['sales'])} | {pct(c['sales'], p['sales'])}")
print(f"판매 건수(행) | {c['lines']}건 | {p['lines']}건 | {c['lines'] - p['lines']:+d}건")
print(f"주문 건수 | {c['orders']}건 | {p['orders']}건 | {pct(c['orders'], p['orders'])}")
print(f"판매 수량 | {c['qty']}개 | {p['qty']}개 | {pct(c['qty'], p['qty'])}")
print(f"객단가 | {won(c['aov'])} | {won(p['aov'])} | {pct(c['aov'], p['aov'])}")

for title, i, top in [("판매채널별", 2, None), ("상위 상품", 4, 5), ("카테고리별", 3, None)]:
    amt, qty, _ = by(cur, i)
    pamt, _, _ = by(prev, i)
    print(f"\n## {title}")
    for k, v in amt.most_common(top):
        print(f"{k} | {won(v)} | {qty[k]}개 | 비중 {v / c['sales'] * 100:.1f}% | {pct(v, pamt.get(k, 0))}")

amt, _, n = by(cur, 0)
print("\n## 일별")
for d in sorted(amt):
    print(f"{d} | {won(amt[d])} | {n[d]}건")
print(f"\n검산: 일별 합 {won(sum(amt.values()))} == 총매출 {won(c['sales'])} -> {sum(amt.values()) == c['sales']}")
