from pyvis.network import Network
from PIL import ImageColor
import networkx as nx


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
