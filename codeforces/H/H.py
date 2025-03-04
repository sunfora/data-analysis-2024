from collections import Counter
from math import log

K_x, K_y = map(int, input().split())
N = int(input())

f = Counter()
fx = Counter()
for i in range(N):
    x, y = [*map(int, input().split())]
    f.update([(x, y)])
    fx.update([x])

result = 0

for x, y in f:
    result -= f[(x, y)] * log(f[(x, y)] / fx[x])

print(result / N)
