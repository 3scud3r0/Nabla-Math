import unittest

from nablamath.optimization import (
    SelfImprovingOptimizer, adam, gradient_descent, newton, rmsprop, simulated_annealing,
)


def bowl(x, y):
    return (x - 2) ** 2 + 3 * (y + 1) ** 2


class OptimizerTests(unittest.TestCase):
    def test_gradient_optimizers_converge_on_quadratic(self):
        for optimizer, kwargs in (
            (gradient_descent, {"learning_rate": 0.1, "steps": 300}),
            (adam, {"learning_rate": 0.08, "steps": 500}),
            (rmsprop, {"learning_rate": 0.05, "steps": 500}),
        ):
            with self.subTest(optimizer=optimizer.__name__):
                trace=optimizer(bowl,(8.0,-6.0),**kwargs)
                self.assertLess(trace.best_value,1e-8)
                self.assertAlmostEqual(trace.best_point[0],2.0,places=3)
                self.assertAlmostEqual(trace.best_point[1],-1.0,places=3)

    def test_newton_uses_second_order_ad(self):
        trace=newton(bowl,(8.0,-6.0),steps=10)
        self.assertTrue(trace.converged)
        self.assertLess(trace.best_value,1e-16)

    def test_annealing_is_seeded_and_bounded(self):
        first=simulated_annealing(lambda x:(x-0.25)**2,((-2.0,2.0),),steps=200,seed=7)
        second=simulated_annealing(lambda x:(x-0.25)**2,((-2.0,2.0),),steps=200,seed=7)
        self.assertEqual(first.points,second.points)
        self.assertEqual(first.values,second.values)
        self.assertLess(first.best_value,1e-3)

    def test_self_improving_search_respects_budget_and_builds_pareto_front(self):
        result=SelfImprovingOptimizer(bowl,(5.0,5.0),budget=6,steps_per_trial=120).run()
        self.assertLessEqual(len(result.trials),6)
        self.assertTrue(result.pareto_frontier)
        self.assertLess(result.best.trace.best_value,1e-6)


if __name__=="__main__":
    unittest.main()
