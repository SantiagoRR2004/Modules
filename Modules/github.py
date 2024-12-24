import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://github.com"
COLOR = "#852fa4"
NUMBERCALLS = 0


def getCorrectURL(url: str) -> str:
    """
    Get the correct URL for a GitHub link

    It will return the URL with the BASE if it doesn't have it.

    Args:
        - url (str): The url to check.

    Returns:
        - str: The correct URL.
    """
    if not url.startswith(BASE):
        return urljoin(BASE, url)
    return url


def getFollowers(username: str) -> list:
    """
    Get the followers of a GitHub user

    Args:
        - username (str): The username to check.

    Returns:
        - list: The list of URLs for the followers.
    """
    web = getCorrectURL(username)

    return getConnection(f"{web}?tab=followers")


def getFollowing(username: str) -> list:
    """
    Get the people that a GitHub user follows

    Args:
        - username (str): The username to check.

    Returns:
        - list: The list of URLs for the people followed.
    """
    web = getCorrectURL(username)

    return getConnection(f"{web}?tab=following")


def getConnection(url: str) -> list:
    """
    Get the people that are in a connection with a GitHub user

    It can be the followers or the people followed.

    Args:
        - url (str): The URL to check.

    Returns:
        - list: The list of URLs for the people in the connection.
    """
    # Initialize an empty list to store the URLs of each
    people = []
    global NUMBERCALLS

    while url:

        response = requests.get(url)
        NUMBERCALLS += 1
        if response.status_code == 200:
            # First we get the body of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Loop through each 'div' element with the class 'd-table' in the HTML content
            for follower in soup.find_all("div", class_="d-table"):

                # Within each 'div' found, search for an 'a' (anchor) tag with the class 'd-inline-block'
                link = follower.find("a", class_="d-inline-block")

                # Check if the anchor tag ('a' tag) exists
                if link:

                    # If found, add the value of the 'href' attribute (the URL) to the people list
                    people.append(urljoin(BASE, link["href"]))

            # Find the 'Next' button link to go to the next page of followers
            next_page = soup.find("a", string="Next")
            # If there is a 'Next' link, update the URL to the next page
            if next_page:
                url = urljoin(BASE, next_page["href"])
            else:
                # No more pages, break the loop
                url = None
        else:
            # If the response status code is not 200, we can't check for the next page
            url = None

    return people


def getRepositories(username: str) -> list:
    """
    Get the repositories of a GitHub user

    It will return them in the format:
        - https://github.com/username/repoName

    Args:
        - username (str): The username to check.

    Returns:
        - list: The list of URLs for the repositories.
    """
    username = getCorrectURL(username)
    global NUMBERCALLS

    url = f"{username}?tab=repositories"

    repositories = []

    while url:
        response = requests.get(url)
        NUMBERCALLS += 1

        soup = BeautifulSoup(response.text, "html.parser")

        # Get the repositories
        repoBlocks = soup.find_all("h3", class_="wb-break-all")

        # Extract the url of the repositories
        for repo in repoBlocks:
            if repo.find("a"):
                repositories.append(urljoin(f"{username}/", repo.find("a").text))

        # Find the 'Next' button link to go to the next page of repositories
        next_page = soup.find("a", string="Next")

        if next_page:
            # If there is a 'Next' link, update the URL to the next page
            url = urljoin(BASE, next_page["href"])
        else:
            # No more pages, break the loop
            url = None

    return repositories


def getContributors(repo: str) -> list:
    """
    Get the contributors of a GitHub repository

    It uses the GitHub API to get the contributors.

    This means it shouldn't be used too much.
    It checks if there are contributors before using the API.
    It stops searching when the page is not filled
    up to 30 contributors.

    It will return them in the format:
        - https://github.com/username

    Args:
        - repo (str): The repository to check.

    Returns:
        - list: The list of URLs for the contributors.
    """
    url = getCorrectURL(repo)
    global NUMBERCALLS

    # First we check that there are contributors to not use the API
    response = requests.get(url)
    NUMBERCALLS += 1
    soup = BeautifulSoup(response.text, "html.parser")

    if not "Contributors" in soup.text:
        return []

    repoUserAndName = "/".join(url.split("/")[-2:])

    contributors = []

    number = 1

    contributorsUrl = f"https://api.github.com/repos/{repoUserAndName}/contributors"

    url = f"{contributorsUrl}?page={number}"

    response = requests.get(url)
    NUMBERCALLS += 1

    while response.status_code == 200 and response.json():

        for i in response.json():
            # We get the URL of the contributor
            contributors.append(i["html_url"])

        if len(response.json()) < 30:
            # If there are less than 30 contributors, we have reached the end
            # We don't continue to reduce the number of API calls
            break

        else:
            number += 1

            url = f"{contributorsUrl}?page={number}"
            response = requests.get(url)
            NUMBERCALLS += 1

    return contributors


def getRealUrlFromAPI(url: str) -> str:
    """
    Get the real URL from a GitHub API URL

    It will return the real URL that is in
    the "html_url" key of the JSON response.

    The given URL must be a GitHub API URL.

    Args:
        - url (str): The URL to check.

    Returns:
        - str: The real URL.
    """
    response = requests.get(url)
    global NUMBERCALLS
    NUMBERCALLS += 1
    return response.json()["html_url"]


def getRepositoryParent(url: str) -> str:
    """
    Get the parent repository of a forked repository

    It will return the parent repository URL or None
    if the repository is not a fork.

    The given URL must be a GitHub repository URL.

    Args:
        - url (str): The URL to check.

    Returns:
        - str: The parent repository URL.
    """
    repository = getCorrectURL(url)

    response = requests.get(repository)
    global NUMBERCALLS
    NUMBERCALLS += 1
    soup = BeautifulSoup(response.text, "html.parser")

    parent = None

    parentLinkMeta = soup.find(
        "meta", {"name": "octolytics-dimension-repository_parent_nwo"}
    )

    if parentLinkMeta:
        parentRepository = parentLinkMeta["content"]
        parent = urljoin(BASE, parentRepository)

    return parent


def getStarredRepositories(username: str) -> list:
    """
    Get the starred repositories of a GitHub user

    It will return them in the format:
        - https://github.com/username/repoName

    Args:
        - username (str): The username to check.

    Returns:
        - list: The list of URLs for the starred repositories.
    """
    username = getCorrectURL(username)
    global NUMBERCALLS

    url = f"{username}?tab=stars"

    repositories = []

    while url:
        response = requests.get(url)
        NUMBERCALLS += 1

        # First we get the body of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Loop through each 'div' element with the class 'col-12 d-block width-full py-4 border-bottom color-border-muted' in the HTML content
        repoContainers = soup.find_all(
            "div",
            class_="col-12 d-block width-full py-4 border-bottom color-border-muted",
        )
        for container in repoContainers:
            link = container.find("h3").find("a")["href"]
            if link:
                # If found, add the value of the 'href' attribute (the URL) to the people list
                repositories.append(link)

        # Find the 'Next' button link to go to the next page of followers
        next_page = soup.find("a", string="Next")

        if next_page:
            # If there is a 'Next' link, update the URL to the next page
            url = urljoin(BASE, next_page["href"])
        else:
            # No more pages, break the loop
            url = None

    return repositories


def getOwner(repository: str) -> str:
    """
    Get the owner of a GitHub repository

    It will return the owner URL in the format:
        - https://github.com/username

    Args:
        - repository (str): The repository to check.

    Returns:
        - str: The URL for the owner.
    """
    repository = getCorrectURL(repository)

    # We just need to eliminate the last part of the URL

    return "/".join(repository.split("/")[:-1])
