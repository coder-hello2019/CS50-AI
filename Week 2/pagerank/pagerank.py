import os
import random
import re
import sys
import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_distribution = {}

    # if page has no outgoing links, return a prob distribution tat chooses randomly among all pages with equal probability
    if len(corpus[page]) == 0:
        for item in corpus:
            prob_distribution[item] = 1/len(corpus)
    else:
        # calculate probabilities for all pages in the corpus
        for item in corpus:
            prob_distribution[item] = (1 - damping_factor)/len(corpus)

        # update probabilities for pages linked on current page
        for item in corpus[page]:
            prob_distribution[item] += damping_factor/len(corpus[page])

    return prob_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = {}
    for page in corpus:
        PageRank[page] = 0

    # pick starting page randomly to kick off the Markov chain
    initial_page = np.random.choice([page for page in corpus])
    # variable to keep track of the page we're currently on
    current_page = initial_page

    for i in range(n):
        # update dict to reflect page we're currently on
        PageRank[current_page] += 1
        # consider probabilities of landing on other pages given the page we're currently on
        next_probabilities = transition_model(corpus, current_page, damping_factor)
        # pick a page given the porbability of picking each page
        next_page = np.random.choice([page for page in next_probabilities.keys()], p = [prob for prob in next_probabilities.values()])
        # update current page
        current_page = next_page

    # normalise results
    for page in PageRank:
        PageRank[page] = PageRank[page]/n

    return PageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = {}
    # dict of T/F flags to keep track of whether PR for any page still needs to be updated (i.e. is the difference between old and new > 0.001)
    update_needed = {}

    # initially set all values to 1/N and mark all pages as needing a PR update
    for page in corpus:
        PageRank[page] = 1 / len(corpus)
        update_needed[page] = True

    # while the difference between old and new is > 0.001
    while any(item for item in update_needed.values()):
        # iterate over pages in corpus
        for page in PageRank:
            # find pages that link to the current page (or pages with no links which we treat as linking to all the pages)
            neighbouring_pages = dict((site, links) for site,links in corpus.items() if page in links or links == set())

            # calculate PRs/weightings for neighbouring pages
            epsilon = 0
            for neighbour in neighbouring_pages:
                # if neighbour links to no pages, interpret the page as having one link for every page in corpus
                if corpus[neighbour] == set():
                     epsilon += (PageRank[neighbour]/len(corpus))
                else:
                    epsilon += (PageRank[neighbour]/len(corpus[neighbour]))
            # calculate new PR and update PR dict
            new_PR = (1 - damping_factor)/len(corpus) + (damping_factor * epsilon)

            # check difference between old and new PR to see if further updates are needed to the page's PR
            old_new_difference = abs(PageRank[page] - new_PR)
            #print(old_new_difference)
            if old_new_difference > 0.001:
                update_needed[page] = True
            else:
                update_needed[page] = False

            # update PR dictionary
            PageRank[page] = new_PR

    # return PR where the difference between old and new values is 0.001 or less
    return PageRank


if __name__ == "__main__":
    main()

    # test_corpus = {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}
    # test_corpus1 = {"1.html": {"2.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}
    # print(f"Sample pagerank result: {sample_pagerank(test_corpus, 0.85, 10)}")
    # print(f"Iterative pagerank result: {iterate_pagerank(test_corpus, 0.85)}")

    #print(transition_model(test_corpus1, "1.html", 0.85))
