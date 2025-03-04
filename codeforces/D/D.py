from collections import defaultdict

K = int(input())
N = int(input())

d = defaultdict(list)

for _ in range(N):
    x, y = map(int, input().split())
    d[x].append(y)

total = 0

for ys in d.values():
    mean = sum(ys) / len(ys)
    total += sum((y - mean) ** 2 for y in ys)

cv = total / N

# Output the result with precision
print(cv)

