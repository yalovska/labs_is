variables = ['A', 'B', 'C', 'D']

domains = {
    'A': ['Червоний', 'Зелений', 'Синій'],
    'B': ['Червоний', 'Зелений', 'Синій'],
    'C': ['Червоний', 'Зелений', 'Синій'],
    'D': ['Червоний', 'Зелений', 'Синій'],
}

# Обмеження: сусіди не можуть мати однаковий колір
constraints = {
    'A': ['B'],
    'B': ['A', 'C', 'D'],
    'C': ['B', 'D'],
    'D': ['B', 'C']
}


# --- Допоміжна функція для перевірки умов ---
def is_consistent(variable, value, assignment, constraints):
    """
    Перевіряє, чи не порушується умова, якщо присвоїти
    'variable' = 'value' при поточних 'assignment'.
    """
    for neighbor in constraints.get(variable, []):
        if neighbor in assignment and assignment[neighbor] == value:
            # Умова порушена! Сусід має такий самий колір.
            return False
    # Жодна з умов не порушується
    return True


# --- 2. Реалізація алгоритму (пошук з поверненням) ---
def solve_csp(assignment, variables, domains, constraints):
    """
    Рекурсивна функція пошуку з поверненням.
    'assignment' - словник з уже присвоєними значеннями.
    """

    # Умова завершення: "Якщо ж ми успішно заповнимо всі параметри..."
    if len(assignment) == len(variables):
        return assignment

    # Крок 1: "вибираємо якийсь один параметрів" (який ще не заповнений)
    var = None
    for v in variables:
        if v not in assignment:
            var = v
            break

    # Крок 2: "...пробуємо підставити будь-яке з допустимих значень"
    for value in domains[var]:

        # Крок 3: "Якщо жодна з умов не порушується..."
        if is_consistent(var, value, assignment, constraints):

            # ...присвоюємо це значення
            assignment[var] = value

            # Крок 4: "...вибираємо наступний параметр" (рекурсивний виклик)
            result = solve_csp(assignment, variables, domains, constraints)

            # Якщо рекурсія повернула повний розв'язок, передаємо його "нагору"
            if result:
                return result

            # Крок 5: "робимо 'відкат', видаляємо присвоєння"
            # Це відбувається, якщо рекурсивний виклик повернув None (зайшов у "тупик")
            del assignment[var]

            # Після "відкату" цикл for автоматично
            # "...пробуємо присвоїти йому інше значення"

    # Крок 6: "Якщо на якомусь кроці... не можемо підставити... жодне значення"
    # Це відбувається, якщо цикл 'for' завершився, і ми нічого не повернули.
    # Ми повертаємо None, сигналізуючи про "тупик".
    return None


# --- 3. Запуск ---

print("Починаємо пошук розв'язку...")
# Починаємо з порожніх присвоєнь
initial_assignment = {}
solution = solve_csp(initial_assignment, variables, domains, constraints)

# --- 4. Результат ---
if solution:
    print("Задачу розв'язано! Знайдено такий набір значень:")
    for variable, value in solution.items():
        print(f"  Параметр '{variable}' = {value}")
else:
    # "Якщо в результаті ми повернемось в початкову вершину..."
    print("Задачу неможливо розв'язати. Жодного розв'язку не існує.")
