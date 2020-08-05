import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()
        print(f"The mines on the board are: {self.mines}")

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # we know the cell is a mine - so we can remote it from set and decrease count accordingly
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # we know the cell is safe - so we can remote it from the set without changing count (if the cell is in the sentence)
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    # helper function to create new inferences based on updated knowledge
    def update_knowledge(self):
        to_remove = []
        new_inferences = []

        for sentence in self.knowledge:
            if sentence.cells == set():
                to_remove.append(sentence)
            for sentence1 in self.knowledge:
                if sentence1.cells == set():
                    to_remove.append(sentence1)

                # only look for inferences if sentences are different
                if sentence != sentence1:
                    # if sentence1 is a subset of sentence
                    if sentence1.cells.issubset(sentence.cells) and len(sentence1.cells) > 0 and len(sentence.cells) > 0:
                        new_inference_cells = sentence.cells - sentence1.cells
                        new_inference_count = sentence.count - sentence1.count
                        if len(new_inference_cells) > 0:
                            new_inference = Sentence(new_inference_cells, new_inference_count)
                            new_inferences.append(new_inference)
                            #print(f"NEW INFERENCE MADE: {new_inference}")
                            #print(f"Sentence that has a subset: {sentence}")
                            #print(f"Sentence that is a subset: {sentence1}")


        #print(f"The new inferences are: {new_inferences_final}")

        # add new sentences to knowledge
        for item in new_inferences:
            if item not in self.knowledge:
                self.knowledge.append(item)

        # remove empty sentences from knowledge
        self.knowledge = [item for item in self.knowledge if len(item.cells) != 0]


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the call as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)

        # create new sentence based on cell and count
        cells_in_sentence = set()

        # Iterate over neighbouring cells (being mindful of the bounds of the board)
        for i in range(max(cell[0] - 1, 0), min(cell[0] + 2, self.height)):
            for j in range(max(cell[1] - 1, 0), min(cell[1] + 2, self.width)):
                # check if the cell is already known as a mine or a safe or if move already made
                if (i, j) not in self.safes and (i, j) not in self.moves_made and (i, j) != cell:
                    # if cell not a known mine or safe, add it to sentence
                    cells_in_sentence.add((i, j))

        # construct new sentence
        new_sentence = Sentence(cells_in_sentence, count)


        #print(f"The new sentence is: {new_sentence}")
        # add new sentence to knowledge
        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        new_safes = set()
        new_mines = set()
        for sentence in self.knowledge:
            if sentence.known_safes() != None:
                new_safes.update(sentence.known_safes())
            if sentence.known_mines() != None:
                new_mines.update(sentence.known_mines())

        for cell in new_safes:
            self.mark_safe(cell)
        for cell in new_mines:
            self.mark_mine(cell)


        #print(f"The new safes are: {new_safes}")
        #print(f"The new mines are: {new_mines}")
        print(f"All the current safes are: {self.safes}")
        print(f"All the current mines are: {self.mines}")

        # infer knew knowledge if possible and add it to AI's knowledge base
        self.update_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # consider all safe moves
        for move in self.safes:
            # ensure that move not already made
            if move not in self.moves_made:
                return move
        # if no safe moves
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_cells = []
        # add cells that haven't been chose yet and are not known to be mines to a list we'll randomly choose from
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    available_cells.append((i, j))

        # return random cell that satisfies the conditions

        if len(available_cells) != 0:
            return random.choice(available_cells)
        else:
            return None
