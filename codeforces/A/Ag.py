import numpy as np

def model(t, params):
    m = np.array([12, 24, 168, 672])
    a0, a1, a2, a3, a4, b1, b2, b3, b4 = params
    return (a0 + a1 * np.sin(2 * np.pi * t / m[0] + b1) +
                 a2 * np.sin(2 * np.pi * t / m[1] + b2) +
                 a3 * np.sin(2 * np.pi * t / m[2] + b3) +
                 a4 * np.sin(2 * np.pi * t / m[3] + b4))

def jacobian(t, params):
    m = np.array([12, 24, 168, 672])
    a0, a1, a2, a3, a4, b1, b2, b3, b4 = params
    jac = np.zeros((len(t), len(params)))

    jac[:, 0] = 1
    jac[:, 1] = np.sin(2 * np.pi * t / m[0] + b1)  
    jac[:, 2] = np.sin(2 * np.pi * t / m[1] + b2)  
    jac[:, 3] = np.sin(2 * np.pi * t / m[2] + b3)  
    jac[:, 4] = np.sin(2 * np.pi * t / m[3] + b4)  
    jac[:, 5] = a1 * np.cos(2 * np.pi * t / m[0] + b1)
    jac[:, 6] = a2 * np.cos(2 * np.pi * t / m[1] + b2)
    jac[:, 7] = a3 * np.cos(2 * np.pi * t / m[2] + b3)
    jac[:, 8] = a4 * np.cos(2 * np.pi * t / m[3] + b4)

    return jac

# Окэй, похоже curve fit использует чот аля Гаус-Ньютон
def gauss_newton(t, y, params_init, max_iter=1000, tol=1e-9):
    params = params_init
    for _ in range(max_iter):
        r = y - model(t, params)
        jac = jacobian(t, params)
    
        d = np.linalg.pinv(jac) @ r 
        params += d

        if np.linalg.norm(d) < tol:
            break
    return params

y = np.zeros(168)
for i in range(168):
    y[i] = int(input())
t = np.arange(1, 169)

# Начальные приближения для параметров

times = 100
cont = np.pad(y, (0, len(y) * (times - 1)))
freq = 2 * np.fft.fft(cont)  / len(cont)

phases = []
amps = []

fs = [12, 24, 168, 672]
for i, f in enumerate(fs):
    id = np.argmin(np.abs(np.fft.fftfreq(168 * times) - 1/f))
    phases.append(np.angle(freq[id]) + np.pi/2)
    amps.append(np.abs(freq[id]) * times)

a0 = np.mean(y)

params_init = np.asarray([a0] + amps + phases)

# Применяем метод Гаусса-Ньютона для оптимизации параметров
params_optimized = gauss_newton(t, y, params_init)
result = model(np.arange(169, 337), params_optimized) 
print(*result, sep="\n")
