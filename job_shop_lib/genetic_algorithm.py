# job_shop_lib/genetic_algorithm.py

import random

class GeneticAlgorithm:
    """
    A class to encapsulate the logic for a Genetic Algorithm solver.
    This class is unchanged from the previous version.
    """
    def __init__(self, fitness_func, population_size, num_genes,
                 crossover_rate=0.8, mutation_rate=0.01, tournament_size=5):
        self.fitness_func = fitness_func
        self.population_size = population_size
        self.num_genes = num_genes
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.population = self._initialize_population()

    def _initialize_population(self):
        population = []
        for _ in range(self.population_size):
            individual = [random.randint(0, 1) for _ in range(self.num_genes)]
            population.append(individual)
        return population

    def _selection(self):
        tournament = random.sample(self.population, self.tournament_size)
        best_individual = max(tournament, key=self.fitness_func)
        return best_individual

    def _crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.num_genes - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2
        return parent1, parent2

    def _mutation(self, individual):
        mutated_individual = []
        for gene in individual:
            if random.random() < self.mutation_rate:
                mutated_individual.append(1 - gene)
            else:
                mutated_individual.append(gene)
        return mutated_individual

    def solve(self, num_generations):
        best_overall_individual = None
        best_overall_fitness = -float('inf')

        print("\n🧬 Starting Genetic Algorithm...")
        for generation in range(num_generations):
            fitness_scores = [self.fitness_func(ind) for ind in self.population]
            best_fitness_in_gen = max(fitness_scores)

            if best_fitness_in_gen > best_overall_fitness:
                best_overall_fitness = best_fitness_in_gen
                best_index = fitness_scores.index(best_fitness_in_gen)
                best_overall_individual = self.population[best_index]

            # Use \r to overwrite the line for a cleaner progress display
            print(f"Generation {generation + 1}/{num_generations} | Best Fitness: {best_overall_fitness}", end='\r')

        print("\n✅ Genetic Algorithm finished.")
        return best_overall_individual, best_overall_fitness


# --- Helper function to get validated user input ---
def get_validated_input(prompt, target_type, min_val=None, max_val=None):
    """A robust function to get and validate user input."""
    while True:
        user_input = input(prompt)
        try:
            value = target_type(user_input)
            if min_val is not None and value < min_val:
                print(f"Error: Value must be at least {min_val}.")
            elif max_val is not None and value > max_val:
                print(f"Error: Value must be no more than {max_val}.")
            else:
                return value
        except ValueError:
            print(f"Error: Invalid input. Please enter a valid {target_type.__name__}.")


# --- Dynamic Example Usage ---
if __name__ == '__main__':
    # Define a simple fitness function (One-Max problem)
    def one_max_fitness(individual):
        return sum(individual)

    print("--- ⚙️ Configure Genetic Algorithm Parameters ---")
    
    # Get user input for GA parameters
    pop_size = get_validated_input("Enter the population size (e.g., 100): ", int, min_val=10)
    genes = get_validated_input("Enter the number of genes per individual (e.g., 50): ", int, min_val=1)
    generations = get_validated_input("Enter the number of generations to run (e.g., 100): ", int, min_val=1)
    cross_rate = get_validated_input("Enter the crossover rate (e.g., 0.8): ", float, min_val=0.0, max_val=1.0)
    mut_rate = get_validated_input("Enter the mutation rate (e.g., 0.01): ", float, min_val=0.0, max_val=1.0)
    
    # Create and run the solver with user-defined parameters
    ga_solver = GeneticAlgorithm(
        fitness_func=one_max_fitness,
        population_size=pop_size,
        num_genes=genes,
        crossover_rate=cross_rate,
        mutation_rate=mut_rate
    )
    
    best_solution, best_score = ga_solver.solve(generations)

    print("\n--- 📊 Results ---")
    print(f"Best solution found: {best_solution}")
    print(f"Fitness score: {best_score} (out of a maximum possible {genes})")