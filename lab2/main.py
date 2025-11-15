class KnowledgeBase:
    def __init__(self):
        # Словники для зберігання прямих зв'язків
        self.is_a_relations = {}
        self.part_of_relations = {}
        self.eats_relations = {}

    def add_is_a(self, child, parent):
        """Додає факт: child Є parent"""
        if child not in self.is_a_relations:
            self.is_a_relations[child] = set()
        self.is_a_relations[child].add(parent)

    def add_part_of(self, part, whole):
        """Додає факт: part Є ЧАСТИНОЮ whole"""
        if part not in self.part_of_relations:
            self.part_of_relations[part] = set()
        self.part_of_relations[part].add(whole)

    def add_eats(self, predator, prey):
        """Додає факт: predator ЇСТЬ prey"""
        if predator not in self.eats_relations:
            self.eats_relations[predator] = set()
        self.eats_relations[predator].add(prey)

    # --- ПРАВИЛА ВИВЕДЕННЯ ---

    def get_all_parents(self, entity, visited=None):
        """
        Рекурсивно знаходить усіх предків сутності через зв'язок is_a.
        """
        if visited is None:
            visited = set()

        parents = self.is_a_relations.get(entity, set())
        all_parents = set(parents)

        for parent in parents:
            if parent not in visited:
                visited.add(parent)
                all_parents.update(self.get_all_parents(parent, visited))

        return all_parents

    def get_all_wholes(self, part, visited=None):
        """
        Рекурсивно знаходить усі об'єкти, частиною яких є part.
        """
        if visited is None:
            visited = set()

        wholes = self.part_of_relations.get(part, set())
        all_wholes = set(wholes)

        for whole in wholes:
            if whole not in visited:
                visited.add(whole)
                all_wholes.update(self.get_all_wholes(whole, visited))

        return all_wholes

    def check_related(self, entity_a, entity_b):
        """
        Головна функція запиту: чи пов'язані A і B?
        Перевіряє is_a, part_of та їх комбінації.
        """
        # 1. Отримуємо всі транзитивні зв'язки для обох сутностей
        parents_a = self.get_all_parents(entity_a)
        parents_b = self.get_all_parents(entity_b)
        wholes_a = self.get_all_wholes(entity_a)
        wholes_b = self.get_all_wholes(entity_b)

        # --- ПЕРЕВІРКА ЗВ'ЯЗКІВ ---

        # А) Пряма ієрархія (A is_a B або B is_a A)
        if entity_b in parents_a or entity_a in parents_b:
            return True, "Зв'язок через ієрархію (IS_A)"

        # Б) Частина-ціле (A part_of B або B part_of A)
        # Перевірка: Чи є A частиною B (або його предків)?
        b_and_ancestors = parents_b | {entity_b}
        if not wholes_a.isdisjoint(b_and_ancestors):
            return True, f"'{entity_a}' є компонентом '{entity_b}' (або його предка)"

        # Перевірка у зворотний бік: Чи є B частиною A?
        a_and_ancestors = parents_a | {entity_a}
        if not wholes_b.isdisjoint(a_and_ancestors):
            return True, f"'{entity_b}' є компонентом '{entity_a}' (або його предка)"

        # В) Харчовий ланцюжок (EATS)
        # Перевіряємо, чи їсть хтось із предків A когось із предків B
        for predator in (parents_a | {entity_a}):
            preys = self.eats_relations.get(predator, set())
            # Чи є серед жертв цього хижака сама сутність B або її предки?
            if not preys.isdisjoint(parents_b | {entity_b}):
                return True, f"Зв'язок через харчування ('{predator}' їсть)"

        return False, "Зв'язку не знайдено"


# =========================================
# ЗАПОВНЕННЯ БАЗИ ЗНАНЬ (ОНТОЛОГІЯ)
# =========================================
kb = KnowledgeBase()

# --- 1. Ієрархія (is_a) ---
# Рівень 1
kb.add_is_a("animal", "organism")
kb.add_is_a("plant", "organism")

# Рівень 2
kb.add_is_a("mammal", "animal")
kb.add_is_a("bird", "animal")
kb.add_is_a("tree", "plant")

# Рівень 3
kb.add_is_a("canine", "mammal")
kb.add_is_a("feline", "mammal")

# Рівень 4 (Практичні класи)
kb.add_is_a("dog", "canine")
kb.add_is_a("cat", "feline")
kb.add_is_a("oak", "tree")

# Екземпляри (Реалізації)
kb.add_is_a("rex", "dog")
kb.add_is_a("buddy", "dog")
kb.add_is_a("barsik", "cat")
kb.add_is_a("old_oak", "oak")

# --- 2. Частини (part_of) ---
kb.add_part_of("head", "animal")
kb.add_part_of("tail", "mammal")
kb.add_part_of("skin", "mammal")
kb.add_part_of("fur", "skin")
kb.add_part_of("leaf", "tree")

# --- 3. Інше (eats) ---
kb.add_eats("canine", "animal")
kb.add_eats("feline", "bird")


# =========================================
# ТЕСТУВАННЯ ЗАПИТІВ
# =========================================

def test_query(a, b):
    result, reason = kb.check_related(a, b)
    status = "✅ ТАК" if result else "❌ НІ"
    print(f"Запит: пов'язані '{a}' і '{b}'? -> {status} ({reason})")


print("\n--- ПОЧАТОК ТЕСТУВАННЯ ---\n")

# 1. Головний тест із завдання
test_query("dog", "fur")
# Очікується: ТАК

# 2. Тест ієрархії (глибокий)
test_query("rex", "organism")
# Очікується: ТАК

# 3. Тест частини (простий)
test_query("tail", "cat")
# Очікується: ТАК

# 4. Тест харчування
test_query("barsik", "bird")
# Очікується: ТАК

# 5. Негативний тест
test_query("dog", "leaf")
# Очікується: НІ

print("\n--- КІНЕЦЬ ТЕСТУВАННЯ ---")
