import numpy as np

K = int(input())
conf_matrix = []

for _ in range(K):
    row = [*map(int, input().split())]
    conf_matrix.append(row)

conf_matrix = np.array(conf_matrix)

prob = conf_matrix.sum(axis=1)
prob = prob / prob.sum()
prob = prob.T

data = []

for i in range(K):
    TP = conf_matrix[i, i]
    FP = np.sum(conf_matrix[:, i]) - TP
    FN = np.sum(conf_matrix[i, :]) - TP
    
    data.append([TP, FP, FN])

data = np.array(data)

TPx, FPx, FNx = data.T

def precision(TP, FP):
    if TP + FP:
        return TP / (TP + FP)
    else:
        return 0

def recall(TP, FN):
    if TP + FN:
        return TP / (TP + FN)
    else:
        return 0

def f_score(*args):
    if len(args) == 3:
        TP, FP, FN = args
        p = precision(TP, FP)
        r = recall(TP, FN)
    else:
        p, r = args
    if p + r:
        return 2 * p * r / (p + r)
    else:
        return 0

def precision_vec(*args):
    return np.asarray([precision(*arg) for arg in zip(*args)])
def recall_vec(*args):
    return np.asarray([recall(*arg) for arg in zip(*args)])
def f_score_vec(*args):
    return np.asarray([f_score(*arg) for arg in zip(*args)])

#print(TPx)
#print(FPx)
#print(FNx)
#print()
#print(precision_vec(TPx, FPx))
#print(recall_vec(TPx, FNx))
#print("f_score", f_score_vec(TPx, FPx, FNx))


microF = f_score(TPx @ prob, FPx @ prob, FNx @ prob)
macroF = f_score(precision_vec(TPx, FPx) @ prob, recall_vec(TPx, FNx) @ prob)
averaF = f_score_vec(TPx, FPx, FNx) @ prob
print(microF)
print(macroF)
print(averaF)
