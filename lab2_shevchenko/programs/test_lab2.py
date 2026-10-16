import unittest
from task1_floor import Floor
from task2_book import Book
from task3_ensemble import Ensemble
from task4_loss import Loss


class FloorTests(unittest.TestCase):
    def test_area_and_tiles(self):
        floor = Floor(6, 5)
        floor.add_obstacle(0.5, 0.5)
        floor.add_obstacle(1, 0.5)
        self.assertEqual(floor.total_area(), 30)
        self.assertEqual(floor.work_area(), 29.25)
        self.assertEqual(floor.tiles_count(0.5, 0.5), 117)
        self.assertEqual(floor.tiles_count(0.6, 0.6), 82)
        self.assertEqual(set(vars(floor)), {'length', 'width', 'obstacles'})

    def test_recalculation(self):
        floor = Floor(3, 4)
        floor.length = 5
        self.assertEqual(floor.work_area(), 20)

    def test_full_exclusion(self):
        floor = Floor(2, 2)
        floor.add_obstacle(2, 2)
        self.assertEqual(floor.tiles_count(1, 1), 0)
        with self.assertRaises(ValueError):
            floor.add_obstacle(1, 1)
        self.assertEqual(len(floor.obstacles), 1)

    def test_invalid(self):
        for value in [0, -1, float('nan'), float('inf'), True, '3']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                Floor(value, 2)
        floor = Floor(2, 2)
        with self.assertRaises(ValueError):
            floor.tiles_count(0, 1)
        with self.assertRaises(ValueError):
            floor.add_obstacle(3, 3)


class BookTests(unittest.TestCase):
    def test_operations(self):
        a, b = Book(300), Book(120)
        self.assertEqual((a + b).pages, 420)
        self.assertEqual((a - b).pages, 180)
        self.assertEqual((a * b).pages, 36000)
        self.assertEqual((a / b).pages, 2)
        for operand in [2, 2.0]:
            self.assertEqual((a + operand).pages, 302)
            self.assertEqual((a - operand).pages, 298)
            self.assertEqual((a * operand).pages, 600)
            self.assertEqual((a / operand).pages, 150)
        self.assertEqual((Book(303) / 2).pages, 152)
        self.assertEqual((Book(301) / 2).pages, 150)
        self.assertEqual(a.pages, 300)

    def test_reading_and_call(self):
        a = Book(300)
        self.assertEqual(a.reading_time(30),
                         'Для прочтения 300 страниц потребуется 10 часов')
        a(450)
        self.assertEqual(a.pages, 450)
        with self.assertRaises(ValueError):
            a(-1)
        self.assertEqual(a.pages, 450)

    def test_invalid(self):
        for value in [1.5, True, '300', None]:
            with self.subTest(value=value), self.assertRaises(TypeError):
                Book(value)
        with self.assertRaises(ValueError):
            Book(-1)
        with self.assertRaises(ValueError):
            Book(3) * 0.5
        with self.assertRaises(ValueError):
            Book(3) - 4
        for op in [lambda a, b: a+b, lambda a, b: a-b,
                   lambda a, b: a*b, lambda a, b: a/b]:
            with self.assertRaises(TypeError):
                op(Book(3), '2')
        for value in [0, Book(0)]:
            with self.assertRaises(ZeroDivisionError):
                Book(3) / value
        for speed in [0, -1, float('nan')]:
            with self.assertRaises(ValueError):
                Book(300).reading_time(speed)


class EnsembleTests(unittest.TestCase):
    def setUp(self):
        self.ensemble = Ensemble()
        for accuracy, time in [(0.8, 10), (0.9, 20), (0.85, 15)]:
            self.ensemble.add_model(accuracy, time)

    def test_totals(self):
        self.assertAlmostEqual(self.ensemble.average_accuracy(), 0.85)
        self.assertEqual(self.ensemble.total_training_time(), 45)

    def test_selection(self):
        self.assertEqual(self.ensemble.optimal_count(0.88), 1)
        self.assertEqual(self.ensemble.optimal_count(0.9), 1)
        self.assertIsNone(self.ensemble.optimal_count(0.95))
        self.assertEqual(len(self.ensemble.models), 3)

    def test_removal(self):
        self.ensemble.remove_model(1)
        self.assertAlmostEqual(self.ensemble.average_accuracy(), 0.825)
        self.assertEqual(self.ensemble.total_training_time(), 25)
        for index in [-1, 20, True]:
            with self.assertRaises(IndexError):
                self.ensemble.remove_model(index)

    def test_empty(self):
        ensemble = Ensemble()
        self.assertEqual(ensemble.average_accuracy(), 0)
        self.assertEqual(ensemble.total_training_time(), 0)
        self.assertIsNone(ensemble.optimal_count(0))

    def test_invalid(self):
        for accuracy, time in [(-0.1, 1), (1.1, 1), (0.5, -1),
                               (float('nan'), 1), (0.5, float('inf'))]:
            with self.assertRaises(ValueError):
                self.ensemble.add_model(accuracy, time)
        self.assertEqual(len(self.ensemble.models), 3)
        with self.assertRaises(ValueError):
            self.ensemble.optimal_count(1.1)


class LossTests(unittest.TestCase):
    def test_operations(self):
        a, b = Loss(0.8), Loss(0.2)
        for operand in [b, 0.2]:
            self.assertAlmostEqual((a + operand).value, 1)
            self.assertAlmostEqual((a - operand).value, 0.6)
            self.assertAlmostEqual((a * operand).value, 0.16)
            self.assertAlmostEqual((a / operand).value, 4)
        self.assertEqual(a.value, 0.8)

    def test_convergence_and_call(self):
        a = Loss(0.8)
        a(0.1)
        self.assertTrue(a.is_converging(Loss(0.2)))
        self.assertFalse(a.is_converging(0.1))
        self.assertFalse(a.is_converging(0.05))
        with self.assertRaises(ValueError):
            a(-1)
        self.assertEqual(a.value, 0.1)

    def test_invalid(self):
        for value in [-1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                Loss(value)
        for value in [True, '0.1', None]:
            with self.assertRaises(TypeError):
                Loss(value)
        with self.assertRaises(ValueError):
            Loss(0.1) - 0.2
        for operand in [0, Loss(0)]:
            with self.assertRaises(ZeroDivisionError):
                Loss(1) / operand
        for op in [lambda a, b: a+b, lambda a, b: a-b,
                   lambda a, b: a*b, lambda a, b: a/b]:
            with self.assertRaises(TypeError):
                op(Loss(1), '2')
        with self.assertRaises(TypeError):
            Loss(1).is_converging('2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
