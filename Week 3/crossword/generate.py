import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        # remove
        #mock_assignment = {Variable(0, 1, 'down', 5): 'SEVEN', Variable(4, 1, 'across', 4): 'NINE', Variable(0, 1, 'across', 3): 'SIX', Variable(1, 4, 'down', 4): 'FIVE'}
        #mock_assignment = {}
        #self.consistent(mock_assignment)


        #self.order_domain_values(Variable(4, 1, 'across', 4), mock_assignment)
        #self.select_unassigned_variable(mock_assignment)
        self.enforce_node_consistency()

        # remove
        #self.revise(Variable(4, 1, 'across', 4), Variable(0, 1, 'down', 5))
        self.ac3()


        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # for each variable, eliminate those values from the domain which do not match the variable's target length
        # take each variable
        for variable in self.domains:
            # take each value in the variable's domain
            toRemove = []

            for value in self.domains[variable]:
                # if length of value is different than length of variable, remove
                if len(value) != variable.length:
                    toRemove.append(value)
            for item in toRemove:
                self.domains[variable].remove(item)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlaps = self.crossword.overlaps[x, y]
        revised = False
        to_remove = set()

        x_domains = self.domains[x]
        y_domains = self.domains[y]

        if overlaps == None:
            return False

        for i in x_domains:
            # if we circle back through all domains of y and don't find a matching one, remove i
            match_in_y = False
            for j in y_domains:
                if i[overlaps[0]] == j[overlaps[1]]:
                    match_in_y = True
            if match_in_y == False:
                to_remove.add(i)
                revised = True

        # remove conflicting words from X's domain
        for word in to_remove:
            self.domains[x].remove(word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Other
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # initial list of all arcs in the problem = all combinations of variables if no list of arcs given
        if(arcs != None):
            queue = arcs
        else:
            queue = []
            for i in self.domains.keys():
                for j in self.domains.keys():
                    # do not create arcs of items with themselves
                    if i == j or (i, j) in queue:
                        pass
                    else:
                        queue.append((i, j))

        while queue:
            arc = queue.pop(0)

            x = arc[0]
            y = arc[1]

            if self.revise(x, y):
                # no possible solution if x's domain is empty
                if self.domains[x] == None:
                    return False
                # if revision made, need to check that new x domain is still consistent with neighbours
                else:
                    for neighbour in (item for item in self.crossword.neighbors(x) if item != y):
                        queue.append((neighbour, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Assignment is complete if every crossword variable has a corresponding item in assignment
        for item in self.crossword.variables:
            if item not in assignment.keys() or assignment[item] == None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check that all words are different, return False if not
        if len(set(assignment.keys())) != len(set(assignment.values())):
            print("Assignment is not consistent because not all values are unique")
            print("The assignment:")
            print(assignment)
            return False

        for item in assignment.keys():
            # check that each word is the correct length
            if item.length != len(assignment[item]):
                print("Assignment is not consistent because the lengths of some values do not match the corresponding variable lengths")
                return False

            # check that no conflicts with neighbours
            print("Neighbours:")
            print(self.crossword.neighbors(item))
            for neighbour in self.crossword.neighbors(item):
                if neighbour in assignment:
                    i, j = self.crossword.overlaps[item, neighbour]

                    if assignment[item][i] != assignment[neighbour][j]:
                        print(f"Assignment is not consistent because {item} conflicts with neighbour {neighbour}")
                        return False

        # consistent if not returned False so far
        print("Assignment is consistent")
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """


        # keys are the values in the domain of var, and values are the numbers of values of neighbouring variables ruled out
        values_ruled_out = {}

        # initiate each value to 0
        for item in self.domains[var]:
            values_ruled_out[item] = 0

        # loop through variable's whole domain
        for varWord in self.domains[var]:
            # loop through variable's neighbours
            for neighbour in self.crossword.neighbors(var):
                if neighbour not in assignment.keys():
                    overlapVar, overlapNeighbour = self.crossword.overlaps[var, neighbour]
                    # loop through neighbour's whole domain
                    for neighWord in self.domains[neighbour]:
                        if (overlapVar >= len(varWord)) or (overlapNeighbour >= len(neighWord)) or (varWord == neighWord) or (varWord[overlapVar] != neighWord[overlapNeighbour]):
                            values_ruled_out[varWord] += 1

        # order the domains from those that eliminate the fewest domains for neighbours
        return [x for x, y in sorted(values_ruled_out.items(), key=lambda x:x[1])]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # list of variables which are not part of assignment
        available_variables = [var for var in self.crossword.variables if var not in assignment.keys()]
        #available_variables = self.crossword.variables - assignment.keys()

        if len(available_variables) == 0:
            print("Returning none")
            return None

        return_variable = available_variables[0]

        for item in available_variables:
            if len(self.domains[item]) < len(self.domains[return_variable]):
                return_variable = item
            # if number of values in domains is the same, pick the variable with the highest degree i.e. how many arcs connect thevariable to other variables, otherwise pick randomly between the two
            elif len(self.domains[item]) == len(self.domains[return_variable]) and len(self.crossword.neighbors(item)) > len(self.crossword.neighbors(return_variable)):
                return_variable = item
            else:
                pass

        print("Return variable: ")
        print(return_variable)
        return return_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # return assignment if it is complete
        if self.assignment_complete(assignment):
            return assignment

        # otherwise, pick a variable and try assigning a value to it
        var = self.select_unassigned_variable(assignment)

        if var is not None:
            for possible_value in self.domains[var]:
                assignment[var] = possible_value
                print(f"Backtrack is considering {possible_value} value for {var} variable")
                # if False is returned further down the line, then the assignment with that value is not possible so we should drop it and assign a new value. Otherwise, the assignment will proceed until the completed assignment is returned.
                if self.consistent(assignment):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
                assignment.pop(var)
        return None

        print("Backtrack would return false")
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)

    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
