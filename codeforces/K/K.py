from heapq import *
from random import randint
def generate_test():
    n = randint(1, 10)
    o = [(randint(1, 10), randint(1, 10)) for _ in range(n)]
    return n, o

# n = int(input())
# o = [(0, 0)] * n
# for i in range(n):
#     o[i] = tuple(map(int, input().split()))

def solution_1(n, o):
    o.sort()

    def dist(x):
        def f(i):
            return abs(o[i][0] - x)
        return f

    sums = [0] * (n + 1)
    for i in range(1, n + 1):
        sums[i] = sums[i - 1] + o[i - 1][1]

    def average(i, j):
        return (sums[j] - sums[i]) / (j - i)


    def find(x, k):
        def wind(i):
            x1 = o[i][0]
            x2 = o[i + k - 1][0]
            return max([abs(x1 - x), abs(x2 - x)])
        l = 0
        r = len(o) - k + 1
        
        if k == n:
            return average(0, n)
         
        # for i in range(r):
        #     print(i, wind(i))
        #     print(o[i:i+k])


        while r - l >= 3:
            # print("l, r =", l, r)
            m1 = l + (r - l) // 3
            m2 = r - (r - l) // 3
            # print("m1, m2 =", m1, m2)
            # print("wind: ", wind(m1), wind(m2))

            if wind(m1) > wind(m2):
                l = m1
            else:
                r = m2
        # print(l, r)
        def valid(i):
            return 0 <= i < n and 0 <= i + k - 1 < n
        res = wind(l)
        ri = l
        for i in range(l, r + 1):
            if valid(i) and wind(i) < res:
                ri = i
                res = wind(i)
        
        # print(l, r)
        if valid(ri - 1) and wind(ri - 1) == wind(ri):
            return -1
        elif valid(ri + 1) and wind(ri + 1) == wind(ri):
            return -1

        return average(ri, ri + k)
    return find
   
def solution_2(n, o):
    def dist(x):
        def f(i):
            return abs(o[i][0] - x)
        return f
     
    def find_nearest(x):
        l = 0
        r = len(o)
        while r - l > 1:
            m = (l + r) // 2
            xm, ym = o[m]
            if xm > x:
                r = m
            else:
                l = m
        if r < n and dist(x)(l) > dist(x)(r):
            return r
        else:
            return l
     
    def find(x, k):
        i = find_nearest(x)
     
        l = i
        r = i
     
        res = o[i][1]
     
        def dst(i):
            if 0 <= i < n:
                return dist(x)(i)
            return float("inf")
     
        # print(o[l:r+1])
        for t in range(1, k):
            # print(o[l:r+1])
            d1 = dst(l - 1) 
            d2 = dst(r + 1) 
            if d2 > d1:
                l = l - 1
                res += o[l][1]
            elif d1 > d2:
                r = r + 1
                res += o[r][1]
            else:
                if t == k:
                    return -1
                l = l - 1
                res += o[l][1]
        print("not so perfec", l, r)
        if l > 0 and dst(l) == dst(l - 1):
            return -1
        if r < n and dst(r) == dst(r + 1):
            return -1
            
        return res / k
    return find

def run_test():
    while True:
        n, o = generate_test()

        bugged = solution_1(n, o)
        perfec = solution_2(n, o)
        
        m = randint(1, 200)
        for _ in range(m):
            x, k = randint(min(o)[0] - 20, max(o)[0] + 20), randint(1, n)
            if bugged(x, k) != perfec(x, k):
                print("Wrong answer", bugged(x, k), perfec(x, k))
                print(n, o)
                print(x, k)
                return [n, o, x, k]

n = int(input())
o = []
for _ in range(n):
    o.append(tuple(map(int, input().split())))
find = solution_1(n, o)
m = int(input())
for _ in range(m):
    x, k = map(int, input().split())
    print(find(x, k))
# n, o, x, k = run_test()
# fixed: n, o, x, k = [5, [(3, 4), (3, 7), (4, 8), (8, 7), (9, 9)], 7, 1]
# print(solution_1(n, o)(x, k))
