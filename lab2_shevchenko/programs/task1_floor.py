"""Задание 1, вариант 2. Расчёт напольного покрытия."""
from math import ceil, isfinite


def positive(value):
    if (type(value) not in (int, float)
            or not isfinite(value) or value <= 0):
        raise ValueError("Размер должен быть числом > 0")
    return float(value)


class Obstacle:
    def __init__(self, width, length):
        self.width = positive(width)
        self.length = positive(length)

    def area(self):
        return self.width * self.length


class Floor:
    def __init__(self, length, width):
        self.length = positive(length)
        self.width = positive(width)
        self.obstacles = []

    def total_area(self):
        return self.length * self.width

    def work_area(self):
        return self.total_area() - sum(
            obstacle.area() for obstacle in self.obstacles)

    def add_obstacle(self, width, length):
        obstacle = Obstacle(width, length)
        if not ((width <= self.width and length <= self.length)
                or (length <= self.width
                    and width <= self.length)):
            raise ValueError("Препятствие не помещается на полу")
        if obstacle.area() > self.work_area():
            raise ValueError("Препятствия больше площади пола")
        self.obstacles.append(obstacle)

    def tiles_count(self, tile_width, tile_length):
        tile_area = positive(tile_width) * positive(tile_length)
        return ceil(self.work_area() / tile_area)


def main():
    print("Расчёт напольного покрытия (размеры в метрах)")
    print("Препятствия не пересекаются; расчёт без запаса.")
    floor = Floor(float(input("Длина пола: ")),
                  float(input("Ширина пола: ")))
    count = int(input("Количество препятствий: "))
    if count < 0:
        raise ValueError("Количество не может быть отрицательным")
    for i in range(count):
        print(f"Препятствие {i + 1}")
        floor.add_obstacle(float(input("Ширина: ")),
                           float(input("Длина: ")))
    width = float(input("Ширина плитки: "))
    length = float(input("Длина плитки: "))
    print(f"Полная площадь пола: {floor.total_area():.2f} м²")
    print(f"Площадь укладки: {floor.work_area():.2f} м²")
    count = floor.tiles_count(width, length)
    print(f"Количество плиток: {count} шт.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OverflowError) as error:
        print(f"Ошибка: {error}")
