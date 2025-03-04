import numpy as np

N = int(input())
x = [0] * N
y = [0] * N
for i in range(N):
    x[i], y[i] = map(int, input().split())

xmap = {xi:i for i, xi in enumerate(sorted(x))}
ymap = {yi:i for i, yi in enumerate(sorted(y))}
Rx = np.array([xmap[xi] for xi in x])
Ry = np.array([ymap[yi] for yi in y])

print(np.corrcoef(Rx, Ry)[0, 1])
