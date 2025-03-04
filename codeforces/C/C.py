from decimal import *
getcontext().prec = 20

N, K = map(int, input().split())
cats = [*map(int, input().split())]
vals = [*map(Decimal, input().split())]

info = {}

total = 0
for cat, val in zip(cats, vals):
    if cat not in info:
        info[cat] = {"cnt": Decimal(0), "sum": Decimal(0)}
    info[cat]["cnt"] += 1
    info[cat]["sum"] += val

ymean = sum(vals) / N

stdy = 0

for v in vals:
    stdy += (v - ymean) ** 2

stdy /= N
stdy **= Decimal(0.5)

result = 0

for cat in info:
    k = info[cat]["cnt"]
    s = info[cat]["sum"]
    stdx = ((k / N) * (1 - k / N)) ** Decimal(0.5)
    if (stdx == 0):
        print(0)
        exit()
    result += k * (s - k * ymean) / N / N / stdy / stdx

print(f"{result:.16f}")
