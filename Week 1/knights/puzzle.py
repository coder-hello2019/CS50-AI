from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    #information about the world
    # A can either be a knight or a knave but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # information about what the characters said
    # for A to be a knight, it must be true that it is a knight and a knave
    # otherwise it's a knave
    Biconditional(AKnight,And(AKnave, AKnight))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # information about the world
    # both A and B can only be a knight or a knaves but not both at once
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),

    # information about what the characters said
    # A is a knight if and only if the sentence is true/the sentence is true if and only if A is a knight
    Biconditional(AKnight, And(AKnave, BKnave)),

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # information about the world
    # both A and B can only be a knight or a knaves but not both at once
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),

    # information about what the character said
    # A is a knight if and only if A and B are of the same kind (else A = knave)
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    # B is a knight if and only if A and B are of diff kinds (else B = knave)
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # information about the world
    # A, B and C can only be a knight or a knave but not both at once
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(CKnight, CKnave)),

    # information about what the characters said
    # if A is a knight, then either of the statements can be true
    Implication(AKnight, Or(AKnight, AKnave)),

    # B is a knight if and only if A said that A is a knave (and A would not say AKnave if it was AKnave)
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),

    # B is a knight if and only if C is a knave (otherwise B is a lying knave)
    Biconditional(BKnight, CKnave),
    # C is a knight if and only if A is a knight (otherwise C is a lying knave)
    Biconditional(CKnight, AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
