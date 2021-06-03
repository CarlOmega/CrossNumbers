# /////////////////////////////////////////////////////////////////////////////////////////////////
# Imports Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
import random
import copy
import sys
import time
# /////////////////////////////////////////////////////////////////////////////////////////////////
# Imports End
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Global Variables Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
# To give value to all the operator to keep pythons order.
order = {'/': 5, '*': 5, '%': 5,
         '+': 4, '-': 4,
         '&': 3,
         '^': 2,
         '|': 1}
# Save if elif in the evaluate function.
operation = {'/': lambda x, y : x // y,
            '*': lambda x, y : x * y,
            '%': lambda x, y : x % y,
            '+': lambda x, y : x + y,
            '-': lambda x, y : x - y,
            '&': lambda x, y : x & y,
            '^': lambda x, y : x ^ y,
            '|': lambda x, y : x | y}
# How many numbers should be removed from each row for given size and diffculty
diffculty_map = {1:{4:1,6:1,8:1,10:1,12:1,14:1,16:1,18:2},
                2:{4:1,6:2,8:2,10:2,12:2,14:2,16:2,18:3},
                3:{4:2,6:3,8:3,10:3,12:3,14:3,16:3,18:4}}
# Printing formats
base_formats = {2: ["{0:<10}", "{0:<10b}", "          "],
                8: ["{0:<5}", "{0:<5o}", "     "],
                10: ["{0:<5}", "{0:<5}", "     "],
                16: ["{0:<5}", "{0:<5x}", "     "]}
# /////////////////////////////////////////////////////////////////////////////////////////////////
# Global Variables End
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////
# evaluate Function Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
def evaluate(e, low, high):
    """Evaluates a string math equation and returns an int of the results.

    Breaks the equation into smaller equations splitting on the operator
    that would be resolved last, and recursivly resolves in post-order.
    Uses a dictionary to keep orders and operators.

    Args:
        e (string): An equation with single digits and {/**%+-&^|}.
        low (int): Index of the first number in the equation.
        high (int): Index of the last number in the equation.

    Returns:
        (int): The answer to the given equation.

    Examples:
        An equation with all digits it can use and all operators.

        >>> equation = "1+2*3/4%5&6^7|9"
        >>> print(evaluate(equation, 0, len(equation)-1))
        13

    """
    if low == high: return int(e[low])  # Base case.
    lowest = low+1
    # Finds last operator to be evaluated (split point).
    for i in range(low+1, high, 2):
        if order[e[i]] <= order[e[lowest]]: lowest = i
    return operation[e[lowest]](evaluate(e, low, lowest-1), evaluate(e, lowest+1, high))
# /////////////////////////////////////////////////////////////////////////////////////////////////
# evaluate Function End
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////
# permutations Function Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
def permutations(numbers, r):
    """Gets a list of permutations of given numbers with limit r.

    Recursivly gets the permutations of smaller limits,
    then adds all new options to lists and returns that.

    Args:
        numbers (int)[]: Numbers options to use in permutations.
        r (int): Limit of size of permutations.

    Returns:
        (int)[][]: List of lists containing ordered numbers.

    Examples:
        permutations of 1, 2, 3.

        >>> print(permutations([1,2,3], 3))
        [[3, 2, 1], [2, 3, 1], [3, 1, 2], [1, 3, 2], [2, 1, 3], [1, 2, 3]]

    """
    if r==1:
        return [[i] for i in numbers]  # Base case.
    else:
        li = []
        last_permutations = permutations(numbers, r-1)
        for i in numbers:
            for j in last_permutations:
                if i not in j:
                    li.append(j+[i])
        return li
# /////////////////////////////////////////////////////////////////////////////////////////////////
# permutations Function End
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Grid Class Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
class Grid:
    """A class to represent the game grid.

    Generates a grid of given parameters where the rows are limited
    to no repeats and the numbers used are 1-9. With random operators
    it generates totals then removes an amount of number (based on diffculty)
    then searches all solutions. If the program determines there is too many
    numbers to look at it regenerates the grid.

    Args:
        size (int): Grid size in range (4,6,8,10,12,14,16,18).
        diffculty (int): Level of diffculty (1,2,3).
        base (int): Number base representation for output.

    Attributes:
        Defaults:
            size (int): Grid size.
            diffculty (int): Level of diffculty.
            base (int): Base representation.
            state (string): State the grid is in.
        Grid:
            solutions [[{((int),(int)): (int)}]]: Grid solutions representation.
            current_grid (string)[][]: Current grid representation.
            grid (string)[][]: Temp grid for validation and testing.
            missing
        Score:
            start_time (float): Time game was started.
            initial_solutions (int): Count of solutions at start.
            initial_unknown (int): Count of unknowns at start.
            hints (int): Count of hints used.
            badmoves (int): Count of bad moves used.
    Printing:
        printing smallest grid it can generate.

        >>> grid = Grid(4, 3, 10)
        >>> print(grid)
        ____________Total Proc. Time: 0.06, Start Game Grid (4 unknown, 1 solutions)______________
             0    1    2    3
        0:   ?    +    ?    14
        1:   &         ^
        2:   ?    ^    ?    5
        3:   4         8

    """


    def __init__(self, size, diffculty, base):
        self.size = size
        self.diffculty = diffculty
        self.base = base
        self.state = "start"
        # Generated Variables
        self.solutions = []
        self.find_grid()
        # Score variables
        self.start_time = time.time()
        self.initial_solutions = self.solution_count
        self.initial_unknown = self.unknown
        self.hints = 0
        self.badmoves = 0


    def find_grid(self):
        """Finds a grid to start with.

        Keeps making grid until there is a grid with a small enough state space.

        """
        # Grid to display.
        self.current_grid = self.gen_grid(self.size, self.diffculty)
        # Temp grid to check solutions with.
        self.grid = copy.deepcopy(self.current_grid)
        while not self.get_solutions():
            self.current_grid = self.gen_grid(self.size, self.diffculty)
            self.grid = copy.deepcopy(self.current_grid)


    def get_solutions(self):
        """Finds all possible solutions to a grid.

        Finds all valid (using evaluate function) number combinations for each row.
        Then using all combinations of rows find all ones where columns are valid.
        Store all solutions and time it finished.

        Returns:
            (bool): False if state space is too large and True if solutions are found.

        """
        # Gets the row possibles to check
        row_possibles = []
        for i in range(self.size//2):
            numbers = list(set([str(x) for x in range(1, 10)])-set(self.current_grid[i*2][:-1]))
            row_possibles.append(permutations(numbers, diffculty_map[self.diffculty][self.size]))
        # Find valid row permutations.
        row_solutions = [[] for i in range(self.size//2)]
        for i in range(0, self.size, 2):
            for j in row_possibles[i//2]:
                entry = dict()
                for k in range(len(self.missing[i])):
                    self.grid[i][self.missing[i][k]] = j[k]
                    entry[(i, self.missing[i][k])] = j[k]
                if self.grid[i][-1] == evaluate("".join(self.grid[i][:-1]), 0, self.size-2):
                    row_solutions[i//2].append(entry)
        # Checks how big the state space would be with this grid.
        state_space = 1
        for i in row_solutions:
            state_space *= len(i)
        print(state_space)
        # if the state space is broken or too large regenerate grid.
        # Generates a grid a lot quicker than search for all solutions
        if state_space > 50000 or state_space == 0:
            return False
        # searchs for rows that lead to a solution (brute force)
        rows = [0 for x in range(len(row_solutions))]
        while rows:
            rows = self.check(row_solutions, rows)
        self.create_time = time.process_time()
        return True


    def check(self, row_solutions, rows):
        """Checks the row solutions given with indexs given.

        Checks the cobination of row_solutions given, and adds it to solutions if valid.
        Then returns a new set of indexs if it has more to check. This stops recursive depth
        becoming too large. Returns False when the last solution has been checked.

        Args:
            row_solutions [[{((int),(int)): (int)}]]: List of valid solutions for each row.
            row (int)[]: Combination of indexs to check.

        Returns:
            (int)[]: Next combination of rows to check.

        """
        # if at the end of the brute force stop the loop
        if rows[-1] == len(row_solutions[-1]):
             return False
        solution = dict()
        # try the combination of row solutions given by rows
        for i in range(len(rows)):
            solution = {**solution, **row_solutions[i][rows[i]]}
        # Check that columns are valid, then add the combination to the solutions
        if self.check_columns(solution):
            self.solutions.append(solution)
            self.solution_count += 1
        # change the cycle of the rows
        rows[0] += 1
        for i in range(len(rows)-1):
            if rows[i] == len(row_solutions[i]):
                rows[i] = 0
                rows[i+1] += 1
        return rows


    def check_columns(self, solution):
        """Checks all the columns of the grid with given solution.

        Loops all columns return false if new evaluated equations don't equal totals.

        Args:
            solution [{((int),(int)): (int)}]: Solution to try.

        Returns:
            (bool): True if all columns are valid.

        """
        # For all the values in the solution dictionary put them into the temp grid
        for (i, j), value in solution.items():
            self.grid[i][j] = value
        # Check the columns to make sure they are valid
        for i in range(self.size//2):
            equation = "".join([self.grid[x][i*2] for x in range(self.size-1)])
            if self.grid[-1][i*2] != evaluate(equation, 0, self.size-2):
                return False
        return True


    def gen_grid(self, size, diffculty):
        """Generates a game grid.

        Generates a random grid with the limits of 1-9 and each row cannot have duplicates.
        Also it randomly picks operators to put in, Then calculates the row/column totals.
        It then randomly removes (puts "?") numbers and stores which locations where removed.

        Args:
            size (int): Size of the grid to generate.
            diffculty (int): Used to determine the amount of numbers to remove from each row.

        Returns:
            grid (string)[][]: Generated grid represented.

        """
        self.solution_count = 0
        self.unknown = 0
        # options for signs
        operators = list(order.keys())
        # number range randomly 1-9 all numbers for a new grid
        numbers = [random.sample(range(1,10),size//2) for x in range(size//2)]
        # generate an empty grid
        grid = [[None]*size for i in range(size)]
        # fill in grid with random numbers and operators
        for i in range(size-1):
            for j in range(size-1):
                if (i%2==0 and j%2==1) or (i%2==1 and j%2==0):
                    grid[i][j] = random.choice(operators)
                elif (i%2==0 and j%2==0):
                    grid[i][j] = str(numbers[i//2][j//2])
        # add totals
        for i in range(size//2):
            grid[i*2][-1] = evaluate("".join(grid[i*2][:-1]), 0, size-2)
            grid[-1][i*2] = evaluate("".join([grid[x][i*2] for x in range(size-1)]), 0, size-2)
        # randomly remove numbers and replace with "?" and count them
        self.missing = dict()
        for i in range(0,size,2):
            for j in random.sample(range(0,size,2), diffculty_map[self.diffculty][self.size]):
                if i in self.missing:
                    self.missing[i].append(j)
                else:
                    self.missing[i] = [j]
                grid[i][j] = "?"
                self.unknown += 1

        # RETURN A NEW Grid
        return grid


    def try_move(self, row, col, val):
        """Test if the given move is valid and part of a solution.

        Checks if there are solutions with the given move,
        Then inserts the move into the grid and updates solutions.
        Otherwise it adds to bad move and returns False.

        Args:
            row (int): Row to insert at.
            col (int): Column to insert at.
            val (int): Value to check in the board.

        Returns:
            (bool): If the move was good or bad.

        """
        new_solutions = []
        # Get all solutions where the move is part of them.
        for solution in self.solutions:
            if (row,col) in solution:
                if int(solution[(row,col)]) == val:
                    new_solutions.append(solution)
        # Check if there is solutions with the move.
        if len(new_solutions) > 0:
            # Update solutions
            self.solutions = new_solutions
            self.solution_count = len(new_solutions)
            # If move is duplicate move ignore it
            if self.current_grid[row][col] == "?":
                self.current_grid[row][col] = val
                self.unknown -= 1
                return True
        # Add one to bad moves for final score.
        self.badmoves += 1
        return False


    def get_hint(self):
        """Puts in a random move that leads to a solution.

        Randomly picks a solution then trys the moves in random order,
        until one is added. Then tells the user a move was added and increments the hints.

        """
        # Gets random solution
        moves = list(self.solutions[random.randint(0,len(self.solutions)-1)].items())
        # suffles moves so it doesnt fill top to bottom (simulates randomness)
        random.shuffle(moves)
        for (i,j), val in moves:
            # NOTE: Double checking to save time but probably not needed
            if self.current_grid[i][j] == "?":
                if self.try_move(i, j, int(val)):
                    print("Value", val, "added at", i, j)
                    self.hints += 1
                    break


    def __str__(self):
        output = "____________"
        if self.state == "start":
            # Starting title
            title = "Total Proc. Time: {0:.2f}, Start Game Grid ({1} unknown, {2} solutions)"
            output += title.format(self.create_time, self.unknown, self.solution_count)
            self.state = "play"
        elif self.state == "finish":
            # Finish title
            # Get score
            base = self.initial_unknown*1000-self.badmoves-self.initial_solutions//2
            score = ((base/((time.time()-self.start_time) + self.hints*10.0*self.size))*diffculty)
            title = "Finish Time: {0:.2f}, Finish Game Grid (Score {1:.0f})"
            output += title.format(time.time()-self.start_time, score)
        else:
            # Title for mid game
            title = "Current Time: {0:.2f}, Current Game Grid ({1} unknown, {2} solutions)"
            output += title.format(time.time()-self.start_time, self.unknown, self.solution_count)
        output += "______________\n     "
        for i in range(self.size):
            output += base_formats[self.base][0].format(i)
        output += "\n"
        # Board display
        for i in range(len(self.current_grid)):
            output += "{0:<5}".format(str(i)+":")
            for j in range(len(self.current_grid[i])):
                if self.current_grid[i][j] != None:
                    k = len(self.current_grid)-1
                    if ((not(i%2 or j%2)) or (i==k or j==k)) and self.current_grid[i][j] != "?":
                        output += base_formats[self.base][1].format(int(self.current_grid[i][j]))
                    else:
                        output += base_formats[self.base][0].format(self.current_grid[i][j])
                else:
                    output += base_formats[self.base][2]
            output += "\n"
        return output
# /////////////////////////////////////////////////////////////////////////////////////////////////
# Grid Class End
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Main Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
# Very basic UI for the game wont go into detail explaining since its simple.
if __name__ == "__main__":
    grid = None
    action = "r"
    while action != "q":
        if action == "r":
            while True:
                try:
                    print("Size 4|6|8|10|12|14|16|18? ", end="")
                    size = int(input())
                    print("Diffculty 1:(Easy)|2:(Medium)|3:(Hard)? ", end="")
                    diffculty = int(input())
                    print("Base? 2|8|10|16? ", end="")
                    base = int(input())
                    if size in range(4,20,2) and diffculty in [1,2,3] and base in [2,8,10,16]:
                        grid = Grid(size, diffculty, base)
                        print(grid)
                        break
                    else:
                        print("Incorrect parameters")
                except:
                    print("Incorrect parameters")
        elif action == "m":
            print("Enter row col value")
            try:
                row, col, value = [i for i in input().split()]
                if grid.try_move(int(row), int(col), int(value, grid.base)):
                    print(grid)
                else:
                    print("Bad move.")
            except:
                print("Bad move.")
        elif action == "h":
            grid.get_hint()
            print(grid)
        else:
            print("Invalid action... Retry.")
        if grid.unknown == 0:
            grid.state = "finish"
            print(grid)
            print("You finished")
            break
        print("Action m:(move)|h:(hint)|r:(restart)|q:(quit)? ")
        action = input()
# /////////////////////////////////////////////////////////////////////////////////////////////////
# Main Start
# /////////////////////////////////////////////////////////////////////////////////////////////////
