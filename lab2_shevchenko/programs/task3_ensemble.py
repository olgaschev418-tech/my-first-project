"""Задание 3, вариант 2. Ансамбль моделей."""
from math import isfinite


def number(value, minimum, maximum=float("inf")):
    if (type(value) not in (int, float) or not isfinite(value)
            or not minimum <= value <= maximum):
        raise ValueError("Число вне допустимого диапазона")
    return float(value)


class Model:
    def __init__(self, accuracy, training_time):
        self.accuracy = number(accuracy, 0, 1)
        self.training_time = number(training_time, 0)


class Ensemble:
    def __init__(self):
        self.models = []

    def add_model(self, accuracy, training_time):
        self.models.append(Model(accuracy, training_time))

    def remove_model(self, index):
        if (type(index) is not int
                or not 0 <= index < len(self.models)):
            raise IndexError("Неверный индекс модели")
        del self.models[index]

    def average_accuracy(self):
        if not self.models:
            return 0.0
        return (sum(m.accuracy for m in self.models)
                / len(self.models))

    def total_training_time(self):
        return sum(m.training_time for m in self.models)

    def optimal_count(self, target):
        target = number(target, 0, 1)
        # Критерий: минимум моделей, средняя точность >= target.
        # Лучшее среднее для k моделей дают k самых точных.
        ordered = sorted(self.models,
                         key=lambda m: m.accuracy, reverse=True)
        total = 0.0
        for count, model in enumerate(ordered, start=1):
            total += model.accuracy
            if total / count >= target:
                return count
        return None

    def display(self):
        if not self.models:
            print("Ансамбль пуст")
        for i, model in enumerate(self.models, start=1):
            print(f"{i}. Точность: {model.accuracy:.2%}; "
                  f"обучение: {model.training_time:g} мин")
        print(f"Средняя точность: {self.average_accuracy():.2%}")
        print(f"Общее время обучения: "
              f"{self.total_training_time():g} мин")


def main():
    ensemble = Ensemble()
    print("Ансамбль моделей")
    while True:
        print("1 — добавить; 2 — удалить; 3 — расчёт; 0 — выход")
        choice = input("Действие: ")
        try:
            if choice == "1":
                ensemble.add_model(
                    float(input("Точность (0–1): ")),
                    float(input("Время обучения (мин): ")))
            elif choice == "2":
                index = int(input("Номер модели: ")) - 1
                ensemble.remove_model(index)
                print("Модель удалена")
            elif choice == "3":
                ensemble.display()
                target = float(input("Целевая точность (0–1): "))
                count = ensemble.optimal_count(target)
                print("Минимум моделей:",
                      count if count is not None
                      else "цель недостижима")
            elif choice == "0":
                break
            else:
                print("Неизвестное действие")
        except (ValueError, TypeError, IndexError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
