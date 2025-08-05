from Modules import steam
import networkx as nx
import copy
import tqdm


def addFriends(
    graph: nx.MultiDiGraph,
    codeWords: list[str] = ["Steam", "User", "Known"],
    newCodeWords: list[str] = ["Steam", "User", "unknownSteam"],
) -> nx.MultiDiGraph:
    """
    Add friends of Steam users to the graph.

    Because it is bidirectional, it will add the friends of the user
    and the user as a friend of the friends.

    It uses searchData["friends"] to check if the friends have been already added.

    Args:
        - graph (nx.MultiDiGraph): The graph to add the friends to.
        - codeWords (list[str]): The words that the nodes must have to be considered.
        - newCodeWords (list[str]): The words that the new nodes will have.

    Returns:
        - nx.MultiDiGraph: The graph with the friends added.
            It is a deep copy of the original graph.
    """
    graph = copy.deepcopy(graph)

    nodes, attributeList = zip(*graph.nodes(data=True))

    # Only search for nodes that are registered
    processedNodes = []
    processedAttributes = []
    for node, attributes in zip(nodes, attributeList):
        if all(word in attributes.get("type", "") for word in codeWords):
            processedNodes.append(node)
            processedAttributes.append(attributes)

    for node, attributes in tqdm.tqdm(
        zip(processedNodes, processedAttributes),
        total=len(processedNodes),
        desc="Adding friends in Steam",
    ):

        if not attributes.get("searchData", False) or not attributes["searchData"].get(
            "friends", False
        ):

            friends = steam.getFriends(node)

            for friend in friends:
                if friend not in graph.nodes():
                    graph.add_node(friend, type=newCodeWords, color=steam.COLOR)

                graph.add_edge(node, friend)
                graph.add_edge(friend, node)

                # We also need to add that we know their friends
                if not graph.nodes[node].get("searchData", False):
                    graph.nodes[node]["searchData"] = {"friends": True}
                else:
                    graph.nodes[node]["searchData"]["friends"] = True

    return graph


def addGames(
    graph: nx.MultiDiGraph,
    codeWords: list[str] = ["Steam", "User", "Known"],
    newCodeWords: list[str] = ["Steam", "Game"],
) -> nx.MultiDiGraph:
    """
    Add games of Steam users to the graph.

    It uses searchData["games"] to check if the games have been already added.

    Args:
        - graph (nx.MultiDiGraph): The graph to add the games to.
        - codeWords (list[str]): The words that the nodes must have to be considered.
        - newCodeWords (list[str]): The words that the new nodes will have.

    Returns:
        - nx.MultiDiGraph: The graph with the games added.
            It is a deep copy of the original graph.
    """
    graph = copy.deepcopy(graph)

    nodes, attributeList = zip(*graph.nodes(data=True))

    # Only search for nodes that have the codeWords
    processedNodes = []
    processedAttributes = []
    for node, attributes in zip(nodes, attributeList):
        if all(word in attributes.get("type", "") for word in codeWords):
            processedNodes.append(node)
            processedAttributes.append(attributes)

    for node, attributes in tqdm.tqdm(
        zip(processedNodes, processedAttributes),
        total=len(processedNodes),
        desc="Adding games in Steam",
    ):

        if not attributes.get("searchData", False) or not attributes["searchData"].get(
            "games", False
        ):

            games = steam.getGames(node)

            for game in games:
                if game not in graph.nodes():
                    graph.add_node(game, type=newCodeWords, color=steam.COLOR_GAMES)

                graph.add_edge(node, game)
                graph.add_edge(game, node)

                # We also need to add that we know their games
                if not graph.nodes[node].get("searchData", False):
                    graph.nodes[node]["searchData"] = {"games": True}
                else:
                    graph.nodes[node]["searchData"]["games"] = True

    return graph
