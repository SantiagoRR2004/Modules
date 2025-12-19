from modules import github
import networkx as nx
import copy
import tqdm


class GitHubGraphManager:
    def __init__(self, edgeLabels: bool = False) -> None:
        """
        Initialize the GitHubGraphManager.

        Args:
            - edgeLabels (bool): Whether to include edge labels in the graph.
        """
        self.edgeLabels = edgeLabels

    def addRepositories(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the repositories for all the nodes that have
        the type "User" in the graph. It adds the repositories
        as their url.

        When we have found all the repository of a user, we mark it
        in the attribute "searchData" with the key "ownedGitHubRepositories"
        so we don't have to search it again.

        We also mark the repository with the key "githubOwner".

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the repositories.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList),
            total=len(nodes),
            desc="Adding owned repositories",
        ):
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

                        if self.edgeLabels:
                            graph.add_edge(node, repo, label="owns")
                        else:
                            graph.add_edge(node, repo)

                        # We also need to add that we know the owner of the repository
                        if not graph.nodes[repo].get("searchData", False):
                            graph.nodes[repo]["searchData"] = {"githubOwner": True}
                        else:
                            graph.nodes[repo]["searchData"]["githubOwner"] = True

                    if attributes.get("searchData", False):
                        graph.nodes[node]["searchData"][
                            "ownedGitHubRepositories"
                        ] = True
                    else:
                        graph.nodes[node]["searchData"] = {
                            "ownedGitHubRepositories": True
                        }

                else:
                    # We have already added the repositories
                    pass

        return graph

    def addContributors(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
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
            - nx.MultiDiGraph: The graph with the contributors.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList), total=len(nodes), desc="Adding contributors"
        ):
            if "Repository" in attributes["type"]:
                if not attributes.get("searchData", False) or not attributes[
                    "searchData"
                ].get("githubContributors", False):
                    contributors = github.getContributors(node)

                    for c in contributors:
                        if c not in graph.nodes():
                            graph.add_node(
                                c, type=("GitHub", "User"), color=github.COLOR
                            )

                        if self.edgeLabels:
                            graph.add_edge(c, node, label="contributes")
                        else:
                            graph.add_edge(c, node)

                    if attributes.get("searchData", False):
                        graph.nodes[node]["searchData"]["githubContributors"] = True
                    else:
                        graph.nodes[node]["searchData"] = {"githubContributors": True}

                else:
                    # We have already added the contributors
                    pass

        return graph

    def addParentsToRepository(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        If the repository is a fork, we add the parent to the graph.

        We mark "searchData" with the key "githubParent" so we don't
        have to search it again.

        When we find a repository that is a fork we continue
        up the chain until we have added the original repository.

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the parents.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList),
            total=len(nodes),
            desc="Adding repositories' parents",
        ):

            tempNode, tempAttributes = node, attributes
            continueFlag = True

            while continueFlag:

                if "Repository" in tempAttributes["type"] and (
                    not tempAttributes.get("searchData", False)
                    or not tempAttributes["searchData"].get("githubParent", False)
                ):
                    parent, type = github.getRepositoryParent(tempNode)

                    if parent:
                        if parent not in graph.nodes():
                            graph.add_node(
                                parent, type=("GitHub", "Repository"), color="blue"
                            )

                        if self.edgeLabels:
                            if type == "fork":
                                graph.add_edge(tempNode, parent, label="forkedFrom")
                            elif type == "template":
                                graph.add_edge(tempNode, parent, label="templateFrom")
                            else:
                                graph.add_edge(tempNode, parent, label="parent")
                        else:
                            graph.add_edge(tempNode, parent)

                    if tempAttributes.get("searchData", False):
                        graph.nodes[tempNode]["searchData"]["githubParent"] = True
                    else:
                        graph.nodes[tempNode]["searchData"] = {"githubParent": True}

                    if parent:
                        tempNode = parent
                        tempAttributes = graph.nodes[parent]

                else:
                    # We have already added the parent or it was a user
                    continueFlag = False

        return graph

    def addUserConnections(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the followers and following for all the nodes that have
        the type "User" in the graph. It adds the followers
        as their url.

        When we have found all the followers of a user, we mark it
        in the attribute "searchData" with the key "githubFollow"

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the followers.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList),
            total=len(nodes),
            desc="Adding following and followers",
        ):
            if "User" in attributes["type"]:
                if not attributes.get("searchData", False) or not attributes[
                    "searchData"
                ].get("githubFollow", False):
                    followers = github.getFollowers(node)

                    for f in followers:
                        if f not in graph.nodes():
                            graph.add_node(
                                f, type=("GitHub", "User"), color=github.COLOR
                            )

                        # Check if the edge already exists to avoid duplicates
                        # This is only valid because between users the only relation is "follows"
                        if not graph.has_edge(f, node):
                            if self.edgeLabels:
                                graph.add_edge(f, node, label="follows")
                            else:
                                graph.add_edge(f, node)

                    following = github.getFollowing(node)

                    for f in following:
                        if f not in graph.nodes():
                            graph.add_node(
                                f, type=("GitHub", "User"), color=github.COLOR
                            )

                        # Check if the edge already exists to avoid duplicates
                        # This is only valid because between users the only relation is "follows"
                        if not graph.has_edge(node, f):
                            if self.edgeLabels:
                                graph.add_edge(node, f, label="follows")
                            else:
                                graph.add_edge(node, f)

                    if attributes.get("searchData", False):
                        graph.nodes[node]["searchData"]["githubFollow"] = True
                    else:
                        graph.nodes[node]["searchData"] = {"githubFollow": True}

                else:
                    # We have already added the followers
                    pass

        return graph

    def addStarredRepositories(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the starred repositories for all the nodes that have
        the type "User" in the graph. It adds the starred repositories
        as their url.

        When we have found all the starred repositories of a user, we mark it
        in the attribute "searchData" with the key "githubStarred"

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the starred repositories.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList),
            total=len(nodes),
            desc="Adding starred repositories",
        ):
            if "User" in attributes["type"]:
                if not attributes.get("searchData", False) or not attributes[
                    "searchData"
                ].get("githubStarred", False):
                    starred = github.getStarredRepositories(node)

                    for s in starred:
                        if s not in graph.nodes():
                            graph.add_node(
                                s, type=("GitHub", "Repository"), color="blue"
                            )

                        if self.edgeLabels:
                            graph.add_edge(node, s, label="starred")
                        else:
                            graph.add_edge(node, s)

                    if attributes.get("searchData", False):
                        graph.nodes[node]["searchData"]["githubStarred"] = True
                    else:
                        graph.nodes[node]["searchData"] = {"githubStarred": True}

                else:
                    # We have already added the starred repositories
                    pass

        return graph

    def addOwners(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the owner of the repository to the graph.

        When we have found the owner of a repository, we mark it
        in the attribute "searchData" with the key "githubOwner"

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the owners.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList), total=len(nodes), desc="Adding repository owner"
        ):
            if "Repository" in attributes["type"] and (
                not attributes.get("searchData", False)
                or not attributes["searchData"].get("githubOwner", False)
            ):
                owner = github.getOwner(node)

                if owner not in graph.nodes():
                    graph.add_node(owner, type=("GitHub", "User"), color=github.COLOR)

                if self.edgeLabels:
                    graph.add_edge(owner, node, label="owns")
                else:
                    graph.add_edge(owner, node)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubOwner"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubOwner": True}

            else:
                # We have already added the owner or it was a user
                pass

        return graph

    def addStargazers(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the stargazers of the repositories to the graph.

        When we have found the stargazers of a repository, we mark it
        in the attribute "searchData" with the key "githubStargazers"

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the stargazers.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList), total=len(nodes), desc="Adding stargazers"
        ):
            if "Repository" in attributes["type"] and (
                not attributes.get("searchData", False)
                or not attributes["searchData"].get("githubStargazers", False)
            ):
                stargazers = github.getStargazers(node)

                for s in stargazers:
                    if s not in graph.nodes():
                        graph.add_node(s, type=("GitHub", "User"), color=github.COLOR)

                    if self.edgeLabels:
                        graph.add_edge(s, node, label="starred")
                    else:
                        graph.add_edge(s, node)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubStargazers"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubStargazers": True}

            else:
                # We have already added the stargazers or it was a user
                pass

        return graph

    def addDependencies(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Add the dependencies of the repositories to the graph.

        When we have found the dependencies of a repository, we mark it
        in the attribute "searchData" with the key "githubDependencies"

        Args:
            - graph (nx.MultiDiGraph): The graph to be modified.

        Returns:
            - nx.MultiDiGraph: The graph with the dependencies.
        """
        graph = copy.deepcopy(graph)

        nodes, attributeList = zip(*graph.nodes(data=True))

        for node, attributes in tqdm.tqdm(
            zip(nodes, attributeList),
            total=len(nodes),
            desc="Adding repositories' dependencies",
        ):
            if "Repository" in attributes["type"] and (
                not attributes.get("searchData", False)
                or not attributes["searchData"].get("githubDependencies", False)
            ):
                dependencies = github.getDependencies(node)

                for d in dependencies:
                    if d not in graph.nodes():
                        graph.add_node(d, type=("GitHub", "Repository"), color="blue")

                    if self.edgeLabels:
                        graph.add_edge(node, d, label="dependsOn")
                    else:
                        graph.add_edge(node, d)

                if attributes.get("searchData", False):
                    graph.nodes[node]["searchData"]["githubDependencies"] = True
                else:
                    graph.nodes[node]["searchData"] = {"githubDependencies": True}

            else:
                # We have already added the dependencies or it was a user
                pass

        return graph
