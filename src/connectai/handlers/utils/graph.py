def topological_sort_util(v, adj, visited) -> list:
    """Sorts the graph topologically by visiting each reachable node from v with
    iterative DFS algorithm.

    Args:
        v: index of a node being visited
        adj: adjacency list of the graph
        visited: a list of visited nodes
    """
    result = []
    stack = [v]

    while len(stack) != 0:
        s = stack.pop()

        if not visited[s]:
            result.append(s)
            visited[s] = True

        i = 0
        while i < len(adj[s]):
            if not visited[adj[s][i]]:
                stack.append(adj[s][i])
            i += 1

    return result
