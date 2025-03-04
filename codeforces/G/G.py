import numpy as np

N, K = map(int, input().split())
obj = np.asarray([*map(int, input().split())]) - 1

i, f = np.unique(obj, return_counts=True)

m = np.zeros((2, K))
m[1][i] = f

s = np.array([0, (m[1]**2).sum()])

for i in range(1, N):
    ds = np.array([
          2 * m[0][obj[i - 1]] + 1,
        - 2 * m[1][obj[i - 1]] + 1])

    m[1][obj[i - 1]] -= 1
    m[0][obj[i - 1]] += 1


    s += ds
    
    t = np.diag([1/i**2, 1/(N - i)**2])

    print((1 - t @ s) @ [i/N, 1 - i/N])
