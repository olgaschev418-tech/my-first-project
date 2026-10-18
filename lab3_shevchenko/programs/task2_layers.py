"""Задание 2. Вариант 2 для ИИ: слои нейросети."""
from itertools import count


class Layer:
    _ids = count(1)

    def __init__(self):
        self.id = next(Layer._ids)


class DenseLayer:
    def forward(self):
        return f"{self.id}-й прямой проход"

    def backward(self):
        return f"{self.id}-й обратный проход"


class ConvolutionalLayer:
    def forward(self):
        return f"{self.id}-й прямой проход"

    def backward(self):
        return f"{self.id}-й обратный проход"


class Dense(Layer, DenseLayer):
    pass


class Conv(Layer, ConvolutionalLayer):
    pass


def main():
    print("Слои нейросети")
    layers = [Dense(), Conv()]
    for layer in layers:
        print(type(layer).__name__ + ": " + layer.forward())
        print(type(layer).__name__ + ": " + layer.backward())
        print("MRO:", " -> ".join(
            c.__name__ for c in type(layer).__mro__))


if __name__ == "__main__":
    main()
