"""Задание 2, вариант 2. Класс Book."""
from math import isfinite


class Book:
    def __init__(self, pages):
        self(pages)

    def __call__(self, pages):
        if type(pages) is not int:
            raise TypeError("Число страниц должно быть целым")
        if pages < 0:
            raise ValueError("Число страниц не может быть < 0")
        self.pages = pages

    @staticmethod
    def _operand(other):
        if isinstance(other, Book):
            return other.pages
        if type(other) in (int, float) and isfinite(other):
            return other
        return NotImplemented

    @staticmethod
    def _result(value):
        if not isfinite(value) or value < 0:
            raise ValueError("Недопустимое количество страниц")
        if value != int(value):
            raise ValueError("Результат должен быть целым числом")
        return Book(int(value))

    def __add__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return self._result(self.pages + value)

    def __sub__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return self._result(self.pages - value)

    def __mul__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        return self._result(self.pages * value)

    def __truediv__(self, other):
        value = self._operand(other)
        if value is NotImplemented:
            return NotImplemented
        if value == 0:
            raise ZeroDivisionError("Деление на ноль")
        result = self.pages / value
        if result < 0:
            raise ValueError("Результат должен быть >= 0")
        return Book(round(result))

    def reading_time(self, speed):
        if (type(speed) not in (int, float)
                or not isfinite(speed) or speed <= 0):
            raise ValueError("Скорость чтения должна быть > 0")
        hours = self.pages / speed
        return (f"Для прочтения {self.pages} страниц "
                f"потребуется {hours:g} часов")

    def __str__(self):
        return f"{self.pages} страниц"


def main():
    print("Класс Book")
    first = Book(int(input("Страниц в первой книге: ")))
    second = Book(int(input("Страниц во второй книге: ")))
    speed = float(input("Скорость чтения (страниц/час): "))
    print(first.reading_time(speed))
    for name, operation in (
            ("Сложение", lambda: first + second),
            ("Вычитание", lambda: first - second),
            ("Умножение на 2", lambda: first * 2),
            ("Деление на 2", lambda: first / 2)):
        try:
            print(f"{name}: {operation()}")
        except (ValueError, ZeroDivisionError) as error:
            print(f"{name}: ошибка — {error}")
    first(int(input("Новое количество страниц первой книги: ")))
    print("После вызова объекта:", first)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OverflowError) as error:
        print(f"Ошибка: {error}")
