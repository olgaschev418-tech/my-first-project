"""Общие требования задания 2: аналитическое ядро и MRO."""
import json
from itertools import count
from math import isfinite, sqrt
from pathlib import Path


class BaseComponent:
    _ids = count(1)

    def __init__(self, metadata=None, **kwargs):
        super().__init__(**kwargs)
        if (metadata is not None
                and not isinstance(metadata, dict)):
            raise TypeError("metadata должен быть словарём")
        self.id = next(BaseComponent._ids)
        self.metadata = dict(metadata or {})
        self.init_trace = ["BaseComponent"]

    def describe(self):
        return f"Компонент {self.id}"


class ValidationMixin:
    @staticmethod
    def validate_number(value):
        if type(value) not in (int, float):
            raise TypeError("Ожидается число, кроме bool")
        if not isfinite(value):
            raise ValueError("Число должно быть конечным")
        return float(value)

    def validate_data(self, xs, ys):
        if not isinstance(xs, (list, tuple)) or not isinstance(
                ys, (list, tuple)):
            raise TypeError("Данные должны быть списками")
        if len(xs) != len(ys) or len(xs) < 2:
            raise ValueError("Нужно >= 2 пары одинаковой длины")
        return ([self.validate_number(x) for x in xs],
                [self.validate_number(y) for y in ys])


class CachingMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}
        self.init_trace.append("CachingMixin")

    def cached(self, key, operation):
        if key in self._cache:
            self.log("cache hit")
            return self._cache[key]
        self._cache[key] = operation()
        self.log("cache miss")
        return self._cache[key]


class LoggingMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = []
        self.init_trace.append("LoggingMixin")

    def log(self, message):
        if not isinstance(message, str):
            raise TypeError("Сообщение должно быть строкой")
        self.events.append(message)


class ReportMixin:
    def export_report(self, report, path=None):
        if not isinstance(report, dict):
            raise TypeError("Отчёт должен быть словарём")
        text = json.dumps(report, ensure_ascii=False,
                          indent=2, allow_nan=False)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        self.log("export JSON")
        return text


class MLModel(ValidationMixin, CachingMixin, LoggingMixin,
              ReportMixin, BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._xs, self._ys = [], []
        self.k = 1
        self._fitted = False
        self.init_trace.append("MLModel")

    def describe(self):
        return super().describe() + " / MLModel"

    def load_data(self, xs, ys):
        xs, ys = self.validate_data(xs, ys)
        self._xs, self._ys = xs, ys
        self._fitted = False
        self._cache.clear()
        self.log("load data")

    def fit(self, k=1):
        if type(k) is not int:
            raise TypeError("k должен быть целым числом")
        if not 1 <= k <= len(self._xs):
            raise ValueError("k вне диапазона [1, число точек]")
        self.k = k
        self._fitted = True
        self._cache.clear()
        self.log(f"fit k={k}")
        return self

    @staticmethod
    def _knn(x, xs, ys, k):
        indices = sorted(range(len(xs)),
                         key=lambda i: (abs(xs[i] - x), i))[:k]
        return sum(ys[i] for i in indices) / k

    def predict(self, x):
        if not self._fitted:
            raise RuntimeError("Сначала обучите модель")
        x = self.validate_number(x)
        return self.cached((self.k, x), lambda: self._knn(
            x, self._xs, self._ys, self.k))

    def metrics(self, xs, ys):
        xs, ys = self.validate_data(xs, ys)
        errors = [self.predict(x) - y for x, y in zip(xs, ys)]
        return {"MAE": sum(abs(e) for e in errors) / len(errors),
                "RMSE": sqrt(sum(e * e for e in errors)
                             / len(errors))}

    def tune_k(self, candidates):
        if not isinstance(candidates, (list, tuple)):
            raise TypeError("Кандидаты k должны быть списком")
        if not candidates or len(self._xs) < 2:
            raise ValueError("Нет данных или кандидатов")
        scores = {}
        for k in candidates:
            if type(k) is not int or not 1 <= k < len(self._xs):
                raise ValueError("Для LOO требуется 1 <= k < n")
            errors = []
            for i, x in enumerate(self._xs):
                xs = self._xs[:i] + self._xs[i + 1:]
                ys = self._ys[:i] + self._ys[i + 1:]
                prediction = self._knn(x, xs, ys, k)
                errors.append((prediction - self._ys[i]) ** 2)
            scores[k] = sum(errors) / len(errors)
        best = min(scores, key=lambda k: (scores[k], k))
        self.fit(best)
        self.log(f"tune k={best}")
        return best, scores


class EconomicIndicator(ValidationMixin, LoggingMixin,
                        ReportMixin, BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_trace.append("EconomicIndicator")

    def describe(self):
        return super().describe() + " / EconomicIndicator"

    def roi(self, revenue, cost):
        revenue = self.validate_number(revenue)
        cost = self.validate_number(cost)
        if cost == 0:
            raise ZeroDivisionError("Затраты равны нулю")
        if cost < 0 or revenue < 0:
            raise ValueError("Выручка и затраты должны быть >= 0")
        result = (revenue - cost) / cost * 100
        self.log("calculate ROI")
        return result

    def interpret(self, roi):
        roi = self.validate_number(roi)
        if roi > 0:
            return "Прибыль"
        if roi < 0:
            return "Убыток"
        return "Безубыточность"


class HybridAnalyzer(MLModel, EconomicIndicator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_trace.append("HybridAnalyzer")

    def describe(self):
        return super().describe() + " / HybridAnalyzer"

    def analyze(self, x, cost):
        revenue = self.predict(x)
        roi = self.roi(revenue, cost)
        return {"id": self.id, "metadata": self.metadata,
                "k": self.k, "predicted_revenue": revenue,
                "cost": cost, "ROI_percent": roi,
                "interpretation": self.interpret(roi)}


def main():
    model = MLModel(metadata={"role": "ML"})
    model.load_data([1, 2, 3], [100, 200, 300])
    model.fit()
    print("MLModel, прогноз для 2:", model.predict(2))
    indicator = EconomicIndicator(metadata={"role": "economy"})
    print("EconomicIndicator, ROI:", indicator.roi(450, 300))
    hybrid = HybridAnalyzer(metadata={"author": "Шевченко О.Н."})
    print("MRO HybridAnalyzer:")
    for cls in type(hybrid).__mro__:
        print("  " + cls.__name__)
    print("Завершение конструкторов (без повторов):")
    for name in hybrid.init_trace:
        print("  " + name)
    print("super():", hybrid.describe())
    hybrid.load_data([1, 2, 3, 4, 5], [100, 200, 300, 400, 500])
    best, scores = hybrid.tune_k([1, 2, 3])
    print("Подбор k по LOO MSE:")
    for k, mse in scores.items():
        print(f"  k={k}: MSE={mse:.2f}")
    print("Выбрано k =", best)
    print("Метрики на обучающих данных:", hybrid.metrics(
        [1, 2, 3, 4, 5], [100, 200, 300, 400, 500]))
    report = hybrid.analyze(6, 300)
    print("Повторный прогноз (кэш):", hybrid.predict(6))
    print("JSON-отчёт:\n" + hybrid.export_report(report))
    print("Журнал:")
    for event in hybrid.events:
        print("  " + event)
    try:
        hybrid.roi(450, 0)
    except ZeroDivisionError as error:
        print("Обработано исключение:", error)


if __name__ == "__main__":
    main()
