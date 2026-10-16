"""Задание 4, вариант 2. Класс Loss."""
from math import isfinite


class Loss:
    def __init__(self, value):
        self(value)

    @staticmethod
    def _number(value):
        if type(value) not in (int, float):
            raise TypeError("Значение должно быть числом")
        if not isfinite(value):
            raise ValueError("Число должно быть конечным")
        return float(value)

    def __call__(self, value):
        value = self._number(value)
        if value < 0:
            raise ValueError("Потери должны быть >= 0")
        self.value = value

    @staticmethod
    def _operand(other):
        if isinstance(other, Loss):
            return other.value
        if type(other) in (int, float):
            return Loss._number(other)
        return NotImplemented

    def __add__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return Loss(self.value + value)

    def __sub__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return Loss(self.value - value)

    def __mul__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return Loss(self.value * value)

    def __truediv__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        if value == 0:
            raise ZeroDivisionError("Деление на ноль")
        return Loss(self.value / value)

    def is_converging(self, previous):
        value = self._operand(previous)
        if value is NotImplemented:
            raise TypeError("Ожидается Loss или число")
        if value < 0:
            raise ValueError("Предыдущие потери должны быть >= 0")
        return self.value < value

    def __str__(self):
        return f"{self.value:g}"


def main():
    print("Класс Loss")
    first = Loss(float(input("Первое значение потерь: ")))
    second = Loss(float(input("Второе значение потерь: ")))
    for name, operation in (
            ("Сложение", lambda: first + second),
            ("Вычитание", lambda: first - second),
            ("Умножение", lambda: first * second),
            ("Деление", lambda: first / second)):
        try:
            print(f"{name}: {operation()}")
        except (ValueError, ZeroDivisionError) as error:
            print(f"{name}: ошибка — {error}")
    first(float(input("Новое значение первых потерь: ")))
    print("После вызова объекта:", first)
    print("Потери уменьшились относительно второго значения:",
          "да" if first.is_converging(second) else "нет")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OverflowError) as error:
        print(f"Ошибка: {error}")
