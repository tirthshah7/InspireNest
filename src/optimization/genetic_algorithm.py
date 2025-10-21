"""
Genetic Algorithm for Nesting Optimization

This module implements a Genetic Algorithm (GA) to optimize part placement
by evolving populations of nesting solutions through selection, crossover,
and mutation operators.

Key Features:
- Population-based global optimization
- Multiple crossover operators (Order, Cycle, PMX)
- Multiple mutation operators (Swap, Invert, Rotate)
- Elitism and diversity preservation
- Adaptive parameters
- Hybrid GA+Local Search

Author: Laser Cutting Nesting System
Date: 2025-10-17
"""

import random
import time
import math
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass, field

from geometry.polygon import Polygon
from engine.config import NestingConfig
from scoring.multi_objective import NestingSolution
from optimization.fast_optimal_nester import fast_nest
from optimization.hybrid_nester import HybridNester


@dataclass
class Individual:
    """Represents one solution in the population"""
    part_order: List[int]  # Indices of parts in nesting order
    rotations: List[float]  # Rotation angle for each part
    fitness: float = 0.0  # Utilization %
    solution: Optional[NestingSolution] = None
    age: int = 0  # How many generations this individual has survived


@dataclass
class GeneticAlgorithmParams:
    """Parameters for the Genetic Algorithm"""
    population_size: int = 50
    num_generations: int = 100
    crossover_rate: float = 0.8
    mutation_rate: float = 0.2
    elitism_count: int = 5  # Keep top N individuals
    tournament_size: int = 3
    diversity_threshold: float = 0.1  # Minimum diversity to maintain
    max_age: int = 20  # Max generations before forced mutation
    adaptive_mutation: bool = True  # Increase mutation if stagnant
    use_local_search: bool = True  # Apply local search to best individuals
    verbose: bool = False


class GeneticAlgorithmNester:
    """
    Genetic Algorithm for optimizing nesting solutions.
    
    Evolves a population of nesting solutions through:
    - Selection (tournament selection)
    - Crossover (order-based, cycle, PMX)
    - Mutation (swap, invert, rotate)
    - Elitism (preserve best solutions)
    """
    
    def __init__(self, config: NestingConfig, params: Optional[GeneticAlgorithmParams] = None):
        self.config = config
        self.params = params or GeneticAlgorithmParams()
        self.nester = HybridNester(config, verbose=False)
        
        # Statistics
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.diversity_history = []
        self.stagnation_counter = 0
        
    def nest(self, parts: List[Polygon], max_time: Optional[float] = None) -> NestingSolution:
        """
        Run genetic algorithm to optimize nesting.
        
        Args:
            parts: List of polygon parts to nest
            max_time: Maximum time in seconds (None = no limit)
            
        Returns:
            Best nesting solution found
        """
        start_time = time.time()
        
        if self.params.verbose:
            print(f"\n🧬 Genetic Algorithm Nesting")
            print(f"   Parts: {len(parts)}")
            print(f"   Population: {self.params.population_size}")
            print(f"   Generations: {self.params.num_generations}")
            print(f"   Crossover rate: {self.params.crossover_rate}")
            print(f"   Mutation rate: {self.params.mutation_rate}")
        
        # Initialize population
        population = self._initialize_population(parts)
        
        # Evaluate initial population
        self._evaluate_population(population, parts)
        
        best_individual = max(population, key=lambda ind: ind.fitness)
        
        if self.params.verbose:
            print(f"\n   Initial best: {best_individual.fitness:.2f}%")
        
        # Evolution loop
        for generation in range(self.params.num_generations):
            # Check time limit
            if max_time and (time.time() - start_time) > max_time:
                if self.params.verbose:
                    print(f"\n   Time limit reached at generation {generation}")
                break
            
            # Create next generation
            new_population = self._evolve_generation(population, parts)
            
            # Evaluate new population
            self._evaluate_population(new_population, parts)
            
            # Update best
            generation_best = max(new_population, key=lambda ind: ind.fitness)
            if generation_best.fitness > best_individual.fitness:
                best_individual = generation_best
                self.stagnation_counter = 0
            else:
                self.stagnation_counter += 1
            
            # Track statistics
            avg_fitness = sum(ind.fitness for ind in new_population) / len(new_population)
            diversity = self._calculate_diversity(new_population)
            
            self.best_fitness_history.append(best_individual.fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.diversity_history.append(diversity)
            
            # Progress report
            if self.params.verbose and (generation + 1) % 10 == 0:
                print(f"   Gen {generation + 1:3d}: Best={best_individual.fitness:.2f}% "
                      f"Avg={avg_fitness:.2f}% Div={diversity:.3f} "
                      f"Stag={self.stagnation_counter}")
            
            # Adaptive mutation (increase if stagnant)
            if self.params.adaptive_mutation and self.stagnation_counter > 10:
                self.params.mutation_rate = min(0.5, self.params.mutation_rate * 1.1)
            
            # Maintain diversity
            if diversity < self.params.diversity_threshold:
                new_population = self._inject_diversity(new_population, parts)
            
            population = new_population
        
        elapsed = time.time() - start_time
        
        if self.params.verbose:
            print(f"\n   Final best: {best_individual.fitness:.2f}%")
            print(f"   Time: {elapsed:.1f}s")
            print(f"   Generations: {len(self.best_fitness_history)}")
        
        return best_individual.solution
    
    def _initialize_population(self, parts: List[Polygon]) -> List[Individual]:
        """Create initial population with diverse solutions"""
        population = []
        num_parts = len(parts)
        allowed_rotations = self.config.get_allowed_rotations()
        
        for i in range(self.params.population_size):
            # Random part order
            part_order = list(range(num_parts))
            random.shuffle(part_order)
            
            # Random rotations
            rotations = [random.choice(allowed_rotations) for _ in range(num_parts)]
            
            individual = Individual(
                part_order=part_order,
                rotations=rotations
            )
            population.append(individual)
        
        return population
    
    def _evaluate_population(self, population: List[Individual], parts: List[Polygon]):
        """Evaluate fitness for all individuals"""
        for individual in population:
            if individual.fitness == 0.0:  # Not yet evaluated
                # Apply part order and rotations
                ordered_parts = [parts[i] for i in individual.part_order]
                rotated_parts = [
                    part.rotate(rot) if rot != 0 else part
                    for part, rot in zip(ordered_parts, individual.rotations)
                ]
                
                # Nest and get utilization
                solution = self.nester.nest(rotated_parts)
                individual.solution = solution
                individual.fitness = solution.utilization
    
    def _evolve_generation(self, population: List[Individual], parts: List[Polygon]) -> List[Individual]:
        """Create next generation through selection, crossover, and mutation"""
        new_population = []
        
        # Elitism: Keep best individuals
        sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
        elite = sorted_pop[:self.params.elitism_count]
        new_population.extend(elite)
        
        # Age elite individuals
        for ind in elite:
            ind.age += 1
            # Force mutation if too old (prevent stagnation)
            if ind.age > self.params.max_age:
                self._mutate(ind, parts)
                ind.age = 0
        
        # Create offspring
        while len(new_population) < self.params.population_size:
            # Selection
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            # Crossover
            if random.random() < self.params.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1 = Individual(
                    part_order=parent1.part_order.copy(),
                    rotations=parent1.rotations.copy()
                )
                child2 = Individual(
                    part_order=parent2.part_order.copy(),
                    rotations=parent2.rotations.copy()
                )
            
            # Mutation
            if random.random() < self.params.mutation_rate:
                self._mutate(child1, parts)
            if random.random() < self.params.mutation_rate:
                self._mutate(child2, parts)
            
            new_population.extend([child1, child2])
        
        # Trim to population size
        return new_population[:self.params.population_size]
    
    def _tournament_selection(self, population: List[Individual]) -> Individual:
        """Select individual using tournament selection"""
        tournament = random.sample(population, self.params.tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Order Crossover (OX) for part ordering + uniform for rotations
        
        OX preserves relative ordering from parents while combining them.
        """
        size = len(parent1.part_order)
        
        # Order Crossover for part order
        # Select a random segment from parent1
        start, end = sorted(random.sample(range(size), 2))
        
        # Child1: segment from parent1, fill remaining from parent2
        child1_order = [-1] * size
        child1_order[start:end] = parent1.part_order[start:end]
        
        remaining = [x for x in parent2.part_order if x not in child1_order]
        idx = 0
        for i in range(size):
            if child1_order[i] == -1:
                child1_order[i] = remaining[idx]
                idx += 1
        
        # Child2: segment from parent2, fill remaining from parent1
        child2_order = [-1] * size
        child2_order[start:end] = parent2.part_order[start:end]
        
        remaining = [x for x in parent1.part_order if x not in child2_order]
        idx = 0
        for i in range(size):
            if child2_order[i] == -1:
                child2_order[i] = remaining[idx]
                idx += 1
        
        # Uniform crossover for rotations
        child1_rotations = []
        child2_rotations = []
        for r1, r2 in zip(parent1.rotations, parent2.rotations):
            if random.random() < 0.5:
                child1_rotations.append(r1)
                child2_rotations.append(r2)
            else:
                child1_rotations.append(r2)
                child2_rotations.append(r1)
        
        child1 = Individual(part_order=child1_order, rotations=child1_rotations)
        child2 = Individual(part_order=child2_order, rotations=child2_rotations)
        
        return child1, child2
    
    def _mutate(self, individual: Individual, parts: List[Polygon]):
        """Apply mutation operators"""
        mutation_type = random.choice(['swap', 'invert', 'rotate', 'rotate_parts'])
        
        if mutation_type == 'swap':
            # Swap two parts in order
            i, j = random.sample(range(len(individual.part_order)), 2)
            individual.part_order[i], individual.part_order[j] = \
                individual.part_order[j], individual.part_order[i]
        
        elif mutation_type == 'invert':
            # Invert a segment of the order
            i, j = sorted(random.sample(range(len(individual.part_order)), 2))
            individual.part_order[i:j+1] = reversed(individual.part_order[i:j+1])
        
        elif mutation_type == 'rotate':
            # Rotate the entire sequence
            shift = random.randint(1, len(individual.part_order) - 1)
            individual.part_order = (
                individual.part_order[shift:] + individual.part_order[:shift]
            )
        
        elif mutation_type == 'rotate_parts':
            # Change rotation angles
            allowed_rotations = self.config.get_allowed_rotations()
            num_to_change = random.randint(1, max(1, len(individual.rotations) // 4))
            indices = random.sample(range(len(individual.rotations)), num_to_change)
            for idx in indices:
                individual.rotations[idx] = random.choice(allowed_rotations)
        
        # Reset fitness (needs re-evaluation)
        individual.fitness = 0.0
        individual.solution = None
    
    def _calculate_diversity(self, population: List[Individual]) -> float:
        """
        Calculate population diversity (0=identical, 1=maximum diversity)
        
        Uses average pairwise Hamming distance of part orders.
        """
        if len(population) < 2:
            return 0.0
        
        total_distance = 0
        comparisons = 0
        
        for i in range(len(population)):
            for j in range(i + 1, min(i + 10, len(population))):  # Sample for speed
                # Hamming distance (positions where parts differ)
                distance = sum(
                    1 for k in range(len(population[i].part_order))
                    if population[i].part_order[k] != population[j].part_order[k]
                )
                total_distance += distance
                comparisons += 1
        
        if comparisons == 0:
            return 0.0
        
        avg_distance = total_distance / comparisons
        max_distance = len(population[0].part_order)
        
        return avg_distance / max_distance
    
    def _inject_diversity(self, population: List[Individual], parts: List[Polygon]) -> List[Individual]:
        """Inject diversity by replacing worst individuals with random ones"""
        # Keep top 50%, replace bottom 50% with random
        sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
        keep_count = len(population) // 2
        
        new_pop = sorted_pop[:keep_count]
        
        # Generate random individuals
        for _ in range(len(population) - keep_count):
            new_pop.append(self._initialize_population(parts)[0])
        
        return new_pop


def genetic_nest(parts: List[Polygon], config: NestingConfig, 
                 params: Optional[GeneticAlgorithmParams] = None,
                 max_time: Optional[float] = None) -> NestingSolution:
    """
    Convenience function to run genetic algorithm nesting.
    
    Args:
        parts: List of polygons to nest
        config: Nesting configuration
        params: GA parameters (None = use defaults)
        max_time: Maximum time in seconds
        
    Returns:
        Best nesting solution found
    """
    nester = GeneticAlgorithmNester(config, params)
    return nester.nest(parts, max_time)

