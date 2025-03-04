import math
from collections import defaultdict

# Чтение входных данных
K = int(input())  # количество классов
lambdaC = list(map(int, input().split()))  # штрафы за ошибки для классов
alpha = int(input())  # интенсивность аддитивного сглаживания
N = int(input())  # количество обучающих сообщений

# Обучающая выборка
train_data = []
word_counts_per_class = defaultdict(lambda: defaultdict(int))  # количество слов по классам
class_counts = [0] * K  # количество сообщений по классам
all_words = set()  # все слова в обучающей выборке

for _ in range(N):
    line = input().split()
    Ci = int(line[0]) - 1  # класс (нумерация с 0)
    Li = int(line[1])  # количество слов
    words = set(line[2:])  # слова в сообщении
    train_data.append((Ci, words))
    
    class_counts[Ci] += 1
    for word in words:
        word_counts_per_class[Ci][word] += 1
        all_words.add(word)

# Количество всех слов в обучающей выборке
V = len(all_words)

M = int(input())  # количество сообщений в тестовой выборке
test_data = []

for _ in range(M):
    line = input().split()
    Lj = int(line[0])  # количество слов
    words = set(line[1:])  # слова в сообщении
    test_data.append(words)

# Априорные вероятности классов
prior_probabilities = [count / N for count in class_counts]

# Оценка вероятности каждого слова для каждого класса
cond_probabilities = defaultdict(lambda: defaultdict(float))

for c in range(K):
    total_words_in_class = sum(word_counts_per_class[c].values())  # сумма всех слов в классе
    for word in all_words:
        cond_probabilities[c][word] = (word_counts_per_class[c][word] + alpha) / \
                                      (total_words_in_class + alpha * V)

# Функция для вычисления вероятности для сообщения
def classify_message(words):
    log_probs = [math.log(prior_probabilities[c]) for c in range(K)]  # логарифм вероятностей классов
    for word in words:
        for c in range(K):
            log_probs[c] += math.log(cond_probabilities[c].get(word, 1e-10))  # учёт слов
    total_log_prob = sum(math.exp(log_prob) for log_prob in log_probs)
    return [math.exp(log_prob) / total_log_prob for log_prob in log_probs]

# Классификация тестовых сообщений
for words in test_data:
    result = classify_message(words)
    print(" ".join(f"{prob:.10f}" for prob in result))
