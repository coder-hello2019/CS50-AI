import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        """for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)"""

    print(joint_probability(people, {'Harry'}, {'James'}, {'James'}))


    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    """print(f"People: {people}")
    print(f"One_gene: {one_gene}")
    print(f"Two_genes: {two_genes}")
    print(f"Have_trait: {have_trait}")"""
    # list to keep track of each individual's probability - will use later to calculate overall JP
    probabilities = {}
    for person in people:
        probabilities[person] = {"total": 0, "gene": 0}
        if person in one_gene:
            probabilities[person]["quant_gene"] = 1
        elif person in two_genes:
            probabilities[person]["quant_gene"] = 2
        else:
            probabilities[person]["quant_gene"] = 0
        if person in have_trait:
            probabilities[person]["has_trait"] = True
        else:
            probabilities[person]["has_trait"] = False
    #print(probabilities)

    # calculate parents first so that we can then use the results for children
    parents = []
    children = []
    for person in people:
        if people[person]["mother"] == None and people[person]["father"] == None:
            parents.append(person)
            probabilities[person]["gene"] = PROBS["gene"][probabilities[person]["quant_gene"]]
            if person in have_trait:
                pass
            else:
                pass
            """if person in one_gene:
                probabilities[person]["gene"] = PROBS[gene][1]
                # multiply by probability of person having gene by probability of having trait to obtain the 'overall' probability for the person
                if person in have_trait:
                    probabilities[person]["total"] = PROBS["gene"][1] * PROBS["trait"][1][True]
                else:
                    robabilities[person]["total"] = PROBS["gene"][1] * PROBS["trait"][1][False]
            elif person in two_genes:
                probabilities[person]["gene"] = PROBS["gene"][2]
                if person in have_trait:
                    probabilities[person]["total"] = PROBS["gene"][2] * PROBS["trait"][2][True]
                else:
                    probabilities[person]["total"] = PROBS["gene"][2] * PROBS["trait"][2][False]
            elif person not in one_gene and person not in two_genes:
                probabilities[person]["gene"] = PROBS["gene"][0]
                if person in have_trait:
                    probabilities[person]["total"] = PROBS["gene"][0] * PROBS["trait"][0][True]
                else:
                    probabilities[person]["total"] = PROBS["gene"][0] * PROBS["trait"][0][False]"""
        else:
            children.append(person)

    for person in children:
        # keep track of parents' genes in the problem
        mother = people[person]["mother"]
        father = people[person]["father"]
        parent_genes = {mother: 0, father: 0}
        # calculate probs of parents passing genes to child
        # CAN WE FACTOR OUT THIS CODE TO BE LESS UGLY?
        for parent in mother, father:
            # if parent has two genes, will pass 1 unless mutation
            if parent in two_genes:
                parent_genes[parent] = 1 - PROBS["mutation"]
            # if parent has one gene, 50% change of passing and there's still prob of mutation
            elif parent in one_gene:
                parent_genes[parent] = 0.5 - PROBS["mutation"]
            # if parent has no gene, prob of passing is 0 but could still mutate
            else:
                parent_genes[parent] = 0 + PROBS["mutation"]

        # probability of child having one gene
        if person in one_gene:
            # prob that child gets gene from mother and not father
            prob1 = parent_genes[mother] * (1 - parent_genes[father])
            # prob that child gets gene from father and not mother
            prob2 = parent_genes[father] * (1 - parent_genes[mother])
            # prob of person getting the gene is one or the other of above
            probabilities[person]["gene"] = prob1 + prob2
        # prob of child having two genes i.e. that will get one gene from mother AND one from father
        elif person in two_genes:
            probabilities[person]["gene"] = parent_genes[mother] * parent_genes[father]
        # prob of child having no genes i.e. prob that gets no genes from mother AND no genes from father
        else:
            probabilities[person]["gene"] = (1 - parent_genes[mother]) * (1 - parent_genes[father])

        # calculate probability of trait
        probabilities[person]["total"] = probabilities[person]["gene"] * PROBS["trait"][probabilities[person]["quant_gene"]][probabilities[person]["has_trait"]]


    return probabilities



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
