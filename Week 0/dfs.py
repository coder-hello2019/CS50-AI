"""Implemention of DFS for practice purposes"""

# graph consisting of 7 nodes
graph = {"A":["B", "C"], "B": ["D", "E"], "C": ["F", "G"], "D": [""], "E": [""], "F": [""], "G": [""]}
#graph = {"1": ["2", "3"], "2": ["4", "5"], "3": [""], "4": [""], "5": [""]}

# recursive implementation of DFS
def resursiveDFS(graph, start, goal, visited):
    visited.append(start)
    if start == goal:
        print(f"Goal node found, {start}: {goal}")
        print(f"Nodes visited: {visited}")
        return visited

    if graph[start] != [""]:
        for item in graph[start]:
            recursiveDFS(graph=graph, start = item, goal=goal, visited = visited)

# iterative implementation of DFS - using a stack i.e. LIFO
def DFS(graph, start, goal):
    # list to keep track of nodes visited
    visited = []
    # stack to keep track of nodes being considered
    frontier = []
    frontier.append(start)

    while True:
        if frontier == []:
            print("No solution")
            return

        currentNode = frontier.pop()
        visited.append(currentNode)
        print(f"Current node is: {currentNode}")
        if currentNode == goal:
            print(f"Solution found: {currentNode} = {goal}")
            print(visited)
            return
        else:
            if graph[currentNode] != [""]:
                for child in graph[currentNode]:
                    frontier.append(child)

# iterative implementation of BFS - using a queue i.e. FIFO
def BFS(graph, start, goal):
    # list to keep track of nodes visited
    visited = []
    # stack to keep track of nodes being considered
    frontier = []
    frontier.append(start)

    while True:
        if frontier == []:
            print("No solution")
            return

        currentNode = frontier[0]
        frontier = frontier[1:]
        visited.append(currentNode)
        print(f"Current node is: {currentNode}")
        if currentNode == goal:
            print(f"Solution found: {currentNode} = {goal}")
            print(visited)
            return
        else:
            if graph[currentNode] != [""]:
                for child in graph[currentNode]:
                    frontier.append(child)



BFS(graph, start="A", goal="D")
#recursiveDFS(graph=graph, start="1", goal = "3", visited=[])
