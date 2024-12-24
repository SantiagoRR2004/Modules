from pyvis.network import Network
from PIL import ImageColor
import networkx as nx
import copy


def createHTML(graph: nx.MultiDiGraph) -> str:
    """
    Create a HTML file from a graph object.
    It is made for directed graphs.
    When there is a bidirectional edge, it is added only once,
    but with double arrows and the average color of the nodes.

    Args:
        - graph (nx.DiGraph): The graph to be converted.

    Returns:
        str: The HTML.
    """
    graph = removeDuplicateEdges(graph)

    net = Network(directed=True, filter_menu=True, cdn_resources="remote")
    net.set_edge_smooth("dynamic")

    for node, attributes in graph.nodes(data=True):
        # Need to add the standard size of from_nx
        net.add_node(node, **attributes, size=10)

    for u, v, attributes in graph.edges(data=True):
        if (v, u) not in graph.edges():
            # Not bidirectional we add the edge
            net.add_edge(u, v, **attributes)
        # elif (u, v) in net.edges():
        #     # If it has already been added with the same properties
        #     print(net.edges[(u, v)])
        #     if net.edges[(u, v)] == attributes:
        #         pass
        #     else:
        #         # If it hasn't been added with the same properties
        #         net.add_edge(u, v, **attributes)
        elif u < v:
            # Visible in bidirectional without arrow

            color1 = ImageColor.getrgb(graph.nodes[u]["color"])
            color2 = ImageColor.getrgb(graph.nodes[v]["color"])

            color = tuple((c1 + c2) // 2 for c1, c2 in zip(color1, color2))
            colorHex = "#{:02x}{:02x}{:02x}".format(*color)

            net.add_edge(
                u,
                v,
                arrowStrikethrough=False,
                color=colorHex,
                arrows="'to' and 'from' but not m1ddle",
                # https://github.com/WestHealth/pyvis/issues/99
                **attributes,
            )
        else:
            """
            We don't add the edge so it
            doesn't have to do more physics
            """
            pass

    net.show_buttons(filter_=["physics"])
    return net.generate_html()


def removeDuplicateEdges(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Remove the duplicate edges from a graph.
    For an edge to be considered a duplicate, it must have the same
    source and target nodes and the same attributes.

    Args:
        - graph (nx.MultiDiGraph): The graph to be cleaned.

    Returns:
        nx.MultiDiGraph: The cleaned graph.
    """
    cleanedGraph = nx.MultiDiGraph()

    # First we add the nodes
    cleanedGraph.add_nodes_from(graph.nodes(data=True))

    seen = set()

    for u, v, attributes in graph.edges(data=True):
        eTuple = (u, v, tuple(attributes.items()))
        if eTuple not in seen:
            seen.add(eTuple)
            cleanedGraph.add_edge(u, v, **attributes)

    return cleanedGraph


def removeUnconnectedNodes(
    graph: nx.MultiDiGraph, desiredType: str = "Known"
) -> nx.MultiDiGraph:
    """
    Removes the nodes that do are not part
    of a path bewteen two nodes of the desiredType.

    Args:
        - graph (nx.MultiDiGraph): The graph to be cleaned.
        - desiredType (str): The desiredType of the nodes to be kept.

    Returns:
        nx.MultiDiGraph: The cleaned graph.
    """
    cleanedGraph = copy.deepcopy(graph)

    """
    We start by iteratively eliminating all the nodes
    that only have one connection and are not of the desiredType.
    """

    continueFlag = True
    nNodes = len(cleanedGraph.nodes())

    while continueFlag:
        cleanedGraph.remove_nodes_from(
            [
                node
                for node in cleanedGraph
                if len(
                    set(n for n in cleanedGraph.successors(node)).union(
                        set(n for n in cleanedGraph.predecessors(node))
                    )
                )
                < 2
                and desiredType not in cleanedGraph.nodes[node]["type"]
            ]
        )

        if nNodes == len(cleanedGraph.nodes()):
            continueFlag = False

        nNodes = len(cleanedGraph.nodes())

    """
    Now we need to eliminate all the nodes that
    can't reach directly 2 nodes of the desiredType.
    """

    goodNodes = [
        node for node in cleanedGraph if desiredType in cleanedGraph.nodes[node]["type"]
    ]

    notCheckedSymbol = "Not Checked"

    eliminateNodes = {
        node: notCheckedSymbol for node in cleanedGraph if node not in goodNodes
    }

    for n in list(eliminateNodes.keys()):
        if eliminateNodes[n] == notCheckedSymbol:
            goodFoundNodes = set()
            foundNodes = set([n])
            frontier = [n]

            while frontier:
                node = frontier.pop()

                for neighbor in set(cleanedGraph.successors(node)) | set(
                    cleanedGraph.predecessors(node)
                ):

                    if neighbor in goodNodes:
                        # It means there is a path to a desiredType node
                        goodFoundNodes.add(neighbor)

                    elif neighbor not in foundNodes:
                        foundNodes.add(neighbor)
                        frontier.append(neighbor)

                        if (
                            not eliminateNodes[neighbor]
                            and eliminateNodes[neighbor] != notCheckedSymbol
                        ):
                            # The neighbour has been marked as safe
                            # We fill the goodFoundNodes to mark all the foundNodes as not to be eliminated
                            # 2 and 3 are just random numbers
                            goodFoundNodes.add("Garbage 1")
                            goodFoundNodes.add("Garbage 2")

                if len(goodFoundNodes) >= 2:
                    for node in foundNodes:
                        eliminateNodes[node] = False
                    frontier = []

            if len(goodFoundNodes) < 2:
                for node in foundNodes:
                    eliminateNodes[node] = True

    # We check that all the values are booleans
    assert all(isinstance(eliminateNodes[node], bool) for node in eliminateNodes)

    cleanedGraph.remove_nodes_from(
        [node for node in eliminateNodes if eliminateNodes[node]]
    )

    return cleanedGraph
