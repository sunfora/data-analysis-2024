from collections import defaultdict

def smart(x):
    x = [*sorted(x)]
    dp = [0] * (len(x) + 1)
    for i in range(1, len(x)):
        dp[i] = dp[i - 1] + i * (x[i] - x[i - 1])
    return sum(dp) * 2

d = defaultdict(list)
K = int(input())
N = int(input())

for _ in range(N):
    x, y = map(int, input().split())
    d[y].append(x)

values = [d for lst in d.values() for d in lst]

full = smart(values)
intraclass = sum(smart(v) for v in d.values())
interclass = full - intraclass 

print(intraclass)
print(interclass)



def test():
    def dummy(x):
        res = 0
        for i in range(len(x)):
            for j in range(len(x)):
                if i == j:
                    continue
                res += abs(x[i] - x[j])
        return res

    from random import randint

    for test in range(200):
        x = [randint(1, 10) for i in range(200)]
        if dummy(x) == smart(x):
            print(f"test {test} \033[32mpassed\033[0m", end="\r")
        else:
            print(f"falsified: {x}")
    print("Tests passed [\033[32m200\033[0m]")
