import random
import math

# Function to read the TSP file and extract coordinates
def read_tsp_file(filename):
    cities = []
    with open(filename, 'r') as f:
        reading_coordinates = False
        for line in f:
            line = line.strip()
            if line.startswith("NODE_COORD_SECTION"):
                reading_coordinates = True
                continue
            if line.startswith("EOF"):
                break
            if reading_coordinates:
                parts = line.split()
                city_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                cities.append((x, y))
    return cities

# Euclidean distance between two cities
def euclidean_distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

# Calculate the total distance of a route
def total_distance(route, cities):
    distance = 0
    for i in range(len(route) - 1):
        distance += euclidean_distance(cities[route[i]], cities[route[i + 1]])
    distance += euclidean_distance(cities[route[-1]], cities[route[0]])  # Return to start
    return distance
    
def two_opt_neighborhood(tour):
    """
    Generate the 2-opt neighborhood for a given tour.

    :param tour: A list of integers representing the tour (cities).
    :yield: A new tour with a 2-opt swap applied.
    """
    n = len(tour)
    for i in sorted(list(range(0, n - 1)), key= lambda _ : random.random()):  # i starts from 1 to avoid the first city
        for j in sorted(list(range(i + 1, n )), key= lambda _ : random.random()):  # j starts from i + 1 to ensure we don't swap the same edge
            # Create a new tour with the 2-opt swap
            #print(f"{i}--{j}")
            new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
            yield new_tour

# Simulated Annealing with 2-opt
def simulated_annealing(cities, initial_temp, cooling_rate, max_iterations):
    # Start with a random route
    current_route = list(range(len(cities)))
    random.shuffle(current_route)
    current_distance = total_distance(current_route, cities)
    
    best_route = current_route[:]
    best_distance = current_distance
    
    temperature = initial_temp
    
    for iteration in range(max_iterations):
        # Iterate the neighbhorhood. Not standard, og algorithm chooses one.        
        for new_route in two_opt_neighborhood(current_route): 
            # Evaluate the neighbor
            new_distance = total_distance(new_route, cities)            
            # Accept the new solution if it's better or with a probability if worse
            if new_distance < current_distance or random.random() < math.exp((current_distance - new_distance) / temperature):
                current_route = new_route
                current_distance = new_distance                
                # Update the best solution found
                if current_distance < best_distance:
                    best_route = current_route[:]
                    best_distance = current_distance         
        
        # Cool the temperature
        temperature *= cooling_rate
        print(f"Iteration: {iteration} Best distance: {best_distance}")
    
    return best_route, best_distance

# Main function to run the simulated annealing
def main():
    # Read the TSP instance (provide the correct file path for 'ar9152.tsp')
    cities = read_tsp_file('dj38.tsp')  # Adjust the file path as needed
    
    # Set parameters for Simulated Annealing
    initial_temp = 10000  # Starting temperature
    cooling_rate = 0.95  # Cooling rate
    max_iterations = 10000  # Max iterations for the algorithm
    
    # Run simulated annealing with 2-opt
    best_route, best_distance = simulated_annealing(cities, initial_temp, cooling_rate, max_iterations)
    
    # Print the result
    print(f"Best route: {best_route}")
    print(f"Best distance: {best_distance}")

# Run the main function
if __name__ == '__main__':
    main()

