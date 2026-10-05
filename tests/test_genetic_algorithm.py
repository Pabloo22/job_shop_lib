# tests/test_genetic_algorithm.py

import unittest
# Make sure to import your GeneticAlgorithm class
from job_shop_lib.genetic_algorithm import GeneticAlgorithm 

# A simple fitness function for testing purposes
def dummy_fitness(individual):
    return sum(individual)

class TestGeneticAlgorithm(unittest.TestCase):

    def setUp(self):
        """Set up a GA instance before each test."""
        self.ga_solver = GeneticAlgorithm(
            fitness_func=dummy_fitness,
            population_size=10,
            num_genes=8
        )

    def test_initialization(self):
        """Test if the population is initialized correctly."""
        self.assertEqual(len(self.ga_solver.population), 10)
        self.assertEqual(len(self.ga_solver.population[0]), 8)

    def test_solve_returns_valid_output(self):
        """Test if the solve method runs and returns the correct format."""
        num_generations = 5
        best_solution, best_score = self.ga_solver.solve(num_generations)
        
        # Check if the output has the correct length and the score is a number
        self.assertEqual(len(best_solution), 8)
        self.assertIsInstance(best_score, (int, float))

if __name__ == '__main__':
    unittest.main()