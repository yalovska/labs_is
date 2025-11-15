import random, string

# --- НАЛАШТУВАННЯ ---
TARGET = "HELLO GENETIC ALGORITHM"  # Цільова фраза
POP_SIZE = 200  # Розмір популяції
ALPHABET = string.ascii_uppercase + " "  # Дозволені символи (літери + пробіл)


# Функція оцінки (Fitness): кількість співпадінь символів з ціллю
def get_fitness(individual):
    score = 0
    for i in range(len(TARGET)):
        if individual[i] == TARGET[i]:
            score += 1
    return score


# --- ГЕНЕТИЧНИЙ АЛГОРИТМ ---

# 1. Створюємо початкову популяцію (випадкові рядки)
population = []
for _ in range(POP_SIZE):
    ind = ''.join(random.choice(ALPHABET) for _ in range(len(TARGET)))
    population.append(ind)

for generation in range(1000):
    # Сортуємо популяцію від кращих до гірших
    population.sort(key=get_fitness, reverse=True)
    best = population[0]

    print(f"Покоління {generation:3}: {best} (Співпадінь: {get_fitness(best)}/{len(TARGET)})")

    if best == TARGET:
        print("\nЦІЛЬ ДОСЯГНУТО!")
        break

    # Елітизм: 20 найкращих автоматично переходять у нове покоління
    next_generation = population[:20]

    # Генеруємо решту нащадків
    while len(next_generation) < POP_SIZE:
        # Селекція: беремо двох випадкових батьків з топ-50% найкращих
        parent1 = random.choice(population[:POP_SIZE // 2])
        parent2 = random.choice(population[:POP_SIZE // 2])

        # Кросовер: точка розрізу посередині
        mid = len(TARGET) // 2
        child = parent1[:mid] + parent2[mid:]

        # Мутація: з шансом 10% замінюємо ОДИН випадковий символ у дитини
        if random.random() < 0.1:
            char_idx = random.randint(0, len(TARGET) - 1)
            # Замінюємо символ на випадковий з алфавіту
            child = child[:char_idx] + random.choice(ALPHABET) + child[char_idx + 1:]

        next_generation.append(child)

    population = next_generation
