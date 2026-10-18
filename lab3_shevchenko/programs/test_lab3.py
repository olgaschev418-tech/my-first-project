import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from task1_employees import (Employee, Manager, Developer,
                             ManagerSkills, DeveloperSkills, TeamLead)
from task2_layers import (Layer, Dense, Conv, DenseLayer,
                          ConvolutionalLayer)
from analytics_core import (BaseComponent, ValidationMixin,
                            CachingMixin, LoggingMixin, ReportMixin,
                            MLModel, EconomicIndicator, HybridAnalyzer)


class EmployeeTests(unittest.TestCase):
    def test_work_and_mixed_group(self):
        group = [Manager(), Developer(), Manager(), Developer()]
        self.assertEqual(len({e.id for e in group}), 4)
        self.assertEqual([e.work() for e in group], [
            f'{group[0].id}-й управляет',
            f'{group[1].id}-й программирует',
            f'{group[2].id}-й управляет',
            f'{group[3].id}-й программирует'])
        self.assertIsInstance(group[0], Employee)
        self.assertIsInstance(group[0], ManagerSkills)

    def test_explicit_resolution(self):
        lead = TeamLead()
        self.assertEqual(lead.work(), ManagerSkills.work(lead)
                         + '; ' + DeveloperSkills.work(lead))
        self.assertEqual(TeamLead.__mro__, (
            TeamLead, Employee, ManagerSkills, DeveloperSkills, object))

    def test_left_parent_and_reversed_order(self):
        class First(Employee, ManagerSkills, DeveloperSkills):
            pass
        class Second(Employee, DeveloperSkills, ManagerSkills):
            pass
        first, second = First(), Second()
        self.assertEqual(first.work(), ManagerSkills.work(first))
        self.assertEqual(second.work(), DeveloperSkills.work(second))


class LayerTests(unittest.TestCase):
    def test_passes_and_inheritance(self):
        dense, conv = Dense(), Conv()
        self.assertNotEqual(dense.id, conv.id)
        for layer in [dense, conv]:
            self.assertEqual(layer.forward(),
                             f'{layer.id}-й прямой проход')
            self.assertEqual(layer.backward(),
                             f'{layer.id}-й обратный проход')
        self.assertIsInstance(dense, Layer)
        self.assertIsInstance(conv, ConvolutionalLayer)
        self.assertIs(dense.forward.__func__, DenseLayer.forward)
        self.assertIs(conv.forward.__func__, ConvolutionalLayer.forward)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.model = HybridAnalyzer(metadata={'author': 'Шевченко О.Н.'})
        self.model.load_data([1, 2, 3, 4, 5],
                             [100, 200, 300, 400, 500])

    def test_mro_and_single_initialization(self):
        self.assertEqual(HybridAnalyzer.__mro__, (
            HybridAnalyzer, MLModel, EconomicIndicator,
            ValidationMixin, CachingMixin, LoggingMixin,
            ReportMixin, BaseComponent, object))
        original = BaseComponent.__init__
        with patch.object(BaseComponent, '__init__', autospec=True,
                          side_effect=original) as initializer:
            HybridAnalyzer()
            self.assertEqual(initializer.call_count, 1)
        trace = self.model.init_trace
        self.assertEqual(len(trace), len(set(trace)))
        self.assertEqual(trace.count('BaseComponent'), 1)
        self.assertEqual(trace, [
            'BaseComponent', 'LoggingMixin', 'CachingMixin',
            'EconomicIndicator', 'MLModel', 'HybridAnalyzer'])
        self.assertTrue(self.model.describe().endswith(
            'EconomicIndicator / MLModel / HybridAnalyzer'))

    def test_unique_id_and_metadata(self):
        metadata = {'kind': 'test'}
        first = MLModel(metadata=metadata)
        second = EconomicIndicator()
        self.assertNotEqual(first.id, second.id)
        metadata['kind'] = 'changed'
        self.assertEqual(first.metadata['kind'], 'test')
        with self.assertRaises(TypeError):
            BaseComponent(metadata=['wrong'])

    def test_fit_predict_and_tie(self):
        self.model.fit(2)
        self.assertEqual(self.model.predict(6), 450)
        self.assertEqual(self.model.predict(3), 250)
        self.assertEqual(self.model.predict(2.5), 250)
        self.assertEqual(self.model.metrics(
            [1, 2, 3, 4, 5], [100, 200, 300, 400, 500]),
            {'MAE': 50.0, 'RMSE': 50.0})

    def test_tuning_with_held_out_points(self):
        best, scores = self.model.tune_k([1, 2, 3])
        self.assertEqual(best, 2)
        self.assertEqual(scores[1], 10000)
        self.assertEqual(scores[2], 9000)
        self.assertAlmostEqual(scores[3], 18666.666666666668)
        self.assertEqual(self.model.k, 2)
        self.assertEqual(self.model.predict(6), 450)

    def test_cache_hit_and_invalidation(self):
        self.model.fit(2)
        self.model.predict(6)
        self.assertEqual(self.model.events[-1], 'cache miss')
        self.model.predict(6)
        self.assertEqual(self.model.events[-1], 'cache hit')
        self.model.fit(1)
        self.assertEqual(self.model._cache, {})
        self.assertEqual(self.model.predict(6), 500)
        self.model.load_data([1, 2], [10, 20])
        self.assertEqual(self.model._cache, {})
        with self.assertRaises(RuntimeError):
            self.model.predict(6)

    def test_roi_and_interpretation(self):
        self.assertEqual(self.model.roi(450, 300), 50)
        self.assertEqual(self.model.roi(150, 300), -50)
        self.assertEqual(self.model.roi(0, 300), -100)
        self.assertEqual(self.model.interpret(50), 'Прибыль')
        self.assertEqual(self.model.interpret(-50), 'Убыток')
        self.assertEqual(self.model.interpret(0), 'Безубыточность')
        with self.assertRaises(ZeroDivisionError):
            self.model.roi(450, 0)
        with self.assertRaises(ValueError):
            self.model.roi(450, -300)
        with self.assertRaises(ValueError):
            self.model.roi(-1, 300)

    def test_end_to_end_json_export(self):
        self.model.tune_k([1, 2, 3])
        report = self.model.analyze(6, 300)
        self.assertEqual(report['predicted_revenue'], 450)
        self.assertEqual(report['ROI_percent'], 50)
        self.assertEqual(report['interpretation'], 'Прибыль')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.json'
            text = self.model.export_report(report, path)
            self.assertEqual(path.read_text(encoding='utf-8'), text)
            self.assertEqual(json.loads(text), report)
        self.assertEqual(self.model.events[-1], 'export JSON')

    def test_data_validation_and_atomic_update(self):
        invalid = [([], []), ([1], [2]), ([1, 2], [3]),
                   ([1, '2'], [3, 4]), ([True, 2], [3, 4]),
                   ([float('nan'), 2], [3, 4]), ('12', [3, 4])]
        for xs, ys in invalid:
            with self.subTest(xs=xs), self.assertRaises(
                    (ValueError, TypeError)):
                self.model.load_data(xs, ys)
        self.assertEqual(self.model._xs, [1, 2, 3, 4, 5])

    def test_invalid_calls(self):
        with self.assertRaises(RuntimeError):
            self.model.predict(1)
        for k in [True, 1.5, '2', 0, 6]:
            with self.subTest(k=k), self.assertRaises(
                    (ValueError, TypeError)):
                self.model.fit(k)
        for candidates in [[], [0], [5], [True], '123']:
            with self.subTest(candidates=candidates), self.assertRaises(
                    (ValueError, TypeError)):
                self.model.tune_k(candidates)
        self.model.fit()
        for value in [True, '2', None, float('inf')]:
            with self.subTest(value=value), self.assertRaises(
                    (ValueError, TypeError)):
                self.model.predict(value)
        with self.assertRaises(TypeError):
            self.model.log(123)
        with self.assertRaises(TypeError):
            self.model.export_report([])

    def test_incompatible_mro_is_rejected(self):
        class A:
            pass
        class B:
            pass
        class X(A, B):
            pass
        class Y(B, A):
            pass
        with self.assertRaises(TypeError):
            type('InvalidOrder', (X, Y), {})


if __name__ == '__main__':
    unittest.main(verbosity=2)
