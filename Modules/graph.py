from pyvis.network import Network
from PIL import ImageColor
import networkx as nx


def createHTML(graph: nx.DiGraph) -> str:
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
    net = Network(directed=True)

    for node, attributes in graph.nodes(data=True):
        # Need to add the standard size of from_nx
        net.add_node(node, **attributes, size=10)

    for u, v in graph.edges():
        if (v, u) not in graph.edges():
            # Not bidirectional we add the edge
            net.add_edge(u, v)
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
            )
        else:
            # We add the edge as hidden so the physics are the same
            net.add_edge(v, u, hidden=True)

    net.show_buttons(filter_=["physics"])
    return net.generate_html()
