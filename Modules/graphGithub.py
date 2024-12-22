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


def addParentsToRepository(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    If the repository is a fork, we add the parent to the graph.

    We mark "searchData" with the key "githubParent" so we don't
    have to search it again.

    We continue adding until we have the repositories
    that are not forks.

    Args:
        - graph (nx.MultiDiGraph): The graph to be modified.

    Returns:
        nx.MultiDiGraph: The graph with the parents.
    """
    nodes, attributeList = zip(*graph.nodes(data=True))

    for node, attributes in zip(nodes, attributeList):
        if "Repository" in attributes["type"]:
            if not attributes.get("searchData", False) or not attributes[
                "searchData"
            ].get("githubParent", False):
                parent = github.getRepositoryParent(node)

                if parent:
                    if parent not in graph.nodes():
                        graph.add_node(
                            parent, type=("GitHub", "Repository"), color="blue"
                        )
                    graph.add_edge(node, parent)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubParent"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubParent": True}

            else:
                # We have already added the parent
                pass

    if len(nodes) != len(graph.nodes()):
        # We have added a new node
        graph = addParentsToRepository(graph)

    return graph


def addUserConnections(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Add the followers and following for all the nodes that have
    the type "User" in the graph. It adds the followers
    as their url.

    When we have found all the followers of a user, we mark it
    in the attribute "searchData" with the key "githubFollow"

    Args:
        - graph (nx.MultiDiGraph): The graph to be modified.

    Returns:
        nx.MultiDiGraph: The graph with the followers.
    """
    nodes, attributeList = zip(*graph.nodes(data=True))

    for node, attributes in zip(nodes, attributeList):
        if "User" in attributes["type"]:
            if not attributes.get("searchData", False) or not attributes[
                "searchData"
            ].get("githubFollow", False):
                followers = github.getFollowers(node)

                for f in followers:
                    if f not in graph.nodes():
                        graph.add_node(f, type=("GitHub", "User"), color=github.COLOR)
                    graph.add_edge(f, node)

                following = github.getFollowing(node)

                for f in following:
                    if f not in graph.nodes():
                        graph.add_node(f, type=("GitHub", "User"), color=github.COLOR)
                    graph.add_edge(node, f)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubFollow"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubFollow": True}

            else:
                # We have already added the followers
                pass

    return graph


def addStarredRepositories(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Add the starred repositories for all the nodes that have
    the type "User" in the graph. It adds the starred repositories
    as their url.

    When we have found all the starred repositories of a user, we mark it
    in the attribute "searchData" with the key "githubStarred"

    Args:
        - graph (nx.MultiDiGraph): The graph to be modified.

    Returns:
        nx.MultiDiGraph: The graph with the starred repositories.
    """
    nodes, attributeList = zip(*graph.nodes(data=True))

    for node, attributes in zip(nodes, attributeList):
        if "User" in attributes["type"]:
            if not attributes.get("searchData", False) or not attributes[
                "searchData"
            ].get("githubStarred", False):
                starred = github.getStarredRepositories(node)

                for s in starred:
                    if s not in graph.nodes():
                        graph.add_node(s, type=("GitHub", "Repository"), color="blue")
                    graph.add_edge(node, s)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubStarred"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubStarred": True}

            else:
                # We have already added the starred repositories
                pass

    return graph
