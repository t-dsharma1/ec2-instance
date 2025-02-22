import string

from connectai.handlers.utils.graph import topological_sort_util
from genie_dao.datamodel import chatbot_db_model


def extract_context_edges(
    context_map: dict[str, chatbot_db_model.FlowContext], ordered_context_ids: list[str]
) -> list[tuple[int, int]]:
    """
    Build a list of context dependency graph. Iterate over all flow contexts in a dictionary and parse its value to
    find other referenced flow contexts.

    ---
    Given three flow contexts:
    - A (with node index 0) with value "{B}"
    - B (with node index 1) with value "plain string"
    - C (with node index 2) with value "{A}"


    A resulting list of edges would be
    [ (0, 1), (2, 0) ]
    ---

    Args:
        context_map: dict[str, FlowContext] the dictionary of all possible flow contexts
        ordered_context_ids: list[str] a list used to determine indices of nodes in the graph

    Returns:

    """
    edges = []

    node_index_by_context_id = {context_id: node_index for node_index, context_id in enumerate(ordered_context_ids)}

    for i_node_index, i_context_id in enumerate(ordered_context_ids):
        context_value = context_map.get(i_context_id)
        if not context_value:
            raise ValueError(f"context with id {i_context_id} not found in context map")

        depends_on = [tup[1] for tup in string.Formatter().parse(context_value.value or "") if tup[1] is not None]

        for j_context_id in depends_on:
            j_node_index = node_index_by_context_id.get(j_context_id)
            if j_node_index is not None:
                edges.append((j_node_index, i_node_index))

    return edges


def get_context_adjacency_list(context_map: dict[str, chatbot_db_model.FlowContext], ordered_context_ids: list[str]):
    """Builds an adjacency list. Each index of the list is the index of a node and each
    item is a list of successor nodes.

    Given the list:
    [ [1, 2], [2] ]

    We deduce that there are following edges in a DAG:
    - 0 -≥ 1
    - 0 -> 2
    - 1 -> 2


    Args:
        context_map: dict[str, FlowContext] the dictionary of all possible flow contexts
        ordered_context_ids: list[str] a list used to determine indices of nodes in the graph

    Returns:
    """
    edges = extract_context_edges(context_map, ordered_context_ids)
    adjacency_list = [[] for _ in range(len(ordered_context_ids))]

    for i in edges:
        adjacency_list[i[0]].append(i[1])

    return adjacency_list


def sort_context_topologically(
    context_map: dict[str, chatbot_db_model.FlowContext]
) -> list[tuple[str, chatbot_db_model.FlowContext]]:
    """Takes a dictionary of all flow contexts, detects dependencies between them based
    on their presence in the value field, and sorts them in a linear ordering such that
    for every dependency (u, v) from context u to context v, u comes before v in the
    ordering.

    Args:
        context_map: dict[str, FlowContext] the dictionary of all possible flow contexts

    Returns: list[tuple[str, FlowContext]]
    """
    ordered_context_ids = list(context_map.keys())
    num_of_nodes = len(ordered_context_ids)

    stack = []
    visited = [False] * num_of_nodes
    adjacency_list = get_context_adjacency_list(context_map, ordered_context_ids)

    for i in range(num_of_nodes):
        if not visited[i]:
            stack.extend(topological_sort_util(i, adjacency_list, visited))

    result = []
    while stack:
        node_index = stack.pop()
        context_id: str = ordered_context_ids[node_index]
        context = context_map[context_id]
        result.append((context_id, context))

    return result
