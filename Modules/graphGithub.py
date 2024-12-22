import networkx as nx
from Modules import github


def addRepositories(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Add the repositories for all the nodes that have
    the type "User" in the graph. It adds the repositories
    as their url.

    When we have found all the repository of a user, we mark it
    in the attribute "searchData" with the key "ownedGitHubRepositories"
    so we don't have to search it again.

    Args:
        - graph (nx.MultiDiGraph): The graph to be modified.

    Returns:
        nx.MultiDiGraph: The graph with the repositories.
    """
    nodes, attributeList = zip(*graph.nodes(data=True))

    for node, attributes in zip(nodes, attributeList):
        if "User" in attributes["type"]:
            if not attributes.get("searchData", False) or not attributes[
                "searchData"
            ].get("ownedGitHubRepositories", False):
                repositories = github.getRepositories(node)

                for repo in repositories:
                    if repo not in graph.nodes():
                        graph.add_node(
                            repo, type=("GitHub", "Repository"), color="blue"
                        )
                        graph.add_edge(node, repo)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["ownedGitHubRepositories"] = True
                else:
                    graph.nodes[node]["searchData"] = {"ownedGitHubRepositories": True}

            else:
                # We have already added the repositories
                pass

    return graph


def addContributors(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Add the contributors for all the nodes that have
    the type "Repository" in the graph. It adds the contributors
    as their url.

    When we have found all the contributors of a repository, we mark it
    in the attribute "searchData" with the key "githubContributors"
    so we don't have to search it again.

    Args:
        - graph (nx.MultiDiGraph): The graph to be modified.

    Returns:
        nx.MultiDiGraph: The graph with the contributors.
    """
    nodes, attributeList = zip(*graph.nodes(data=True))

    for node, attributes in zip(nodes, attributeList):
        if "Repository" in attributes["type"]:
            if not attributes.get("searchData", False) or not attributes[
                "searchData"
            ].get("githubContributors", False):
                contributors = github.getContributors(node)

                for c in contributors:
                    if c not in graph.nodes():
                        graph.add_node(c, type=("GitHub", "User"), color=github.COLOR)
                        graph.add_edge(c, node)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubContributors"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubContributors": True}

            else:
                # We have already added the contributors
                pass

    return graph
