import numpy as np
from scipy.optimize import curve_fit
import math

y = np.zeros(168)
for i in range(168):
    y[i] = float(input())

t = np.arange(1, 169)

def model(t, a0, a1, a2, a3, a4, b1, b2, b3, b4):
    m = np.array([12, 24, 168, 672])
    return a0 + a1 * np.sin(2 * np.pi * t / m[0] + b1) + a2 * np.sin(2 * np.pi * t / m[1] + b2) + \
           a3 * np.sin(2 * np.pi * t / m[2] + b3) + a4 * np.sin(2 * np.pi * t / m[3] + b4)

# Оценка параметров с помощью curve_fit
params, params_covariance = curve_fit(model, t, y, p0=[0] * 9)

a0, a1, a2, a3, a4, b1, b2, b3, b4 = params

t_future = np.arange(169, 337)
y_future = model(t_future, *params)

for value in y_future:
    print(value)
