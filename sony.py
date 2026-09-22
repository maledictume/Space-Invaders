import matplotlib.pyplot as plt
#import numpy as np

# ==========================================
# 1. ПАРАМЕТРЫ ЗАДАЧИ (Вариант 8)
# ==========================================
alpha = 1.4
a, b = 0.0, 5.0
h = 0.5  # Шаг сетки (можно поменять на 0.1 для более точного расчета)


# Правая часть уравнения и точное решение
def f(x):
    return 1.4 * x ** 3 - 2.8 * x ** 2 + 1.4 * x + 5.6


def exact_sol(x):
    return np.exp(x) + np.exp(-x) - 1.4 * x ** 3 + 2.8 * x ** 2 - 9.8 * x


# Константа для правого краевого условия: y'(5) + y(5) = R
R = 2 * np.exp(5) - 172 * alpha


# ==========================================
# 2. МЕТОД СТРЕЛЬБЫ (Рунге-Кутта 4 + Хорды)
# ==========================================
def rk4_step(x, y_vec, h):
    # y_vec = [y, y']
    def G(x, Y):
        return np.array([Y[1], Y[0] + f(x)])

    k1 = G(x, y_vec)
    k2 = G(x + h / 2, y_vec + h / 2 * k1)
    k3 = G(x + h / 2, y_vec + h / 2 * k2)
    k4 = G(x + h, y_vec + h * k3)
    return y_vec + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def shoot(mu, h):
    N = int(round((b - a) / h))
    x_vals = np.linspace(a, b, N + 1)
    Y = np.zeros((N + 1, 2))
    Y[0] = [2.0, mu]  # Начальные условия: y(0)=2, y'(0)=mu

    for i in range(N):
        Y[i + 1] = rk4_step(x_vals[i], Y[i], h)

    # Считаем невязку на правом конце
    residual = Y[-1][1] + Y[-1][0] - R
    return residual, x_vals, Y[:, 0]


# Метод хорд для поиска правильного угла "выстрела" mu
mu_prev = 0.0
mu_curr = -5.0
F_prev, _, _ = shoot(mu_prev, h)

for _ in range(10):
    F_curr, x_shoot, y_shoot = shoot(mu_curr, h)
    if abs(F_curr) < 1e-7:
        break
    mu_next = mu_curr - F_curr * (mu_curr - mu_prev) / (F_curr - F_prev)
    mu_prev, mu_curr = mu_curr, mu_next
    F_prev = F_curr

# ==========================================
# 3. МЕТОД ПРОГОНКИ (Конечные разности)
# ==========================================
N = int(round((b - a) / h))
x_fdm = np.linspace(a, b, N + 1)
alph = np.zeros(N + 1)
beta = np.zeros(N + 1)

# Левое условие y(0) = 2
alph[1] = 0.0
beta[1] = 2.0

# Прямой ход прогонки
for i in range(1, N):
    F_i = -h ** 2 * f(x_fdm[i])
    C_i = 2.0 + h ** 2

    alph[i + 1] = 1.0 / (C_i - 1.0 * alph[i])
    beta[i + 1] = (F_i + 1.0 * beta[i]) / (C_i - 1.0 * alph[i])

# Правое условие (аппроксимация по 3 узлам)
f_Nminus1 = f(x_fdm[N - 1])
num = 2 * h * R - h ** 2 * f_Nminus1 - (h ** 2 - 2) * beta[N]
den = 2 + 2 * h + (h ** 2 - 2) * alph[N]
y_N = num / den

y_fdm = np.zeros(N + 1)
y_fdm[N] = y_N

# Обратный ход прогонки
for i in range(N - 1, -1, -1):
    y_fdm[i] = alph[i + 1] * y_fdm[i + 1] + beta[i + 1]

# ==========================================
# 4. ПОСТРОЕНИЕ ГРАФИКА
# ==========================================
x_exact = np.linspace(a, b, 200)
y_exact = exact_sol(x_exact)

plt.figure(figsize=(10, 6))

# Рисуем точное решение сплошной линией
plt.plot(x_exact, y_exact, 'k-', linewidth=2, label='Точное аналитическое решение')

# Рисуем метод прогонки синими точками
plt.plot(x_fdm, y_fdm, 'bs--', markersize=6, alpha=0.8, label=f'Метод прогонки (h={h})')

# Рисуем метод стрельбы красными точками
plt.plot(x_shoot, y_shoot, 'ro:', markersize=5, alpha=0.8, label=f'Метод стрельбы (h={h})')

# Оформление графика
plt.title('Сравнение численных методов решения краевой задачи (Вариант 8)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)

# Показываем график
plt.tight_layout()
plt.show()