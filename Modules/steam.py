from urllib.parse import urljoin, urlparse
from typing import List
import requests
from bs4 import BeautifulSoup
import re

BASE = "https://steamcommunity.com/"
COLOR = "#2a475e"

NORMALCALLS = 0
APICALLS = 0


def getCorrectPersonURL(username: str) -> str:
    """
    Get the correct URL for a Steam user profile.

    It needs to be in one of the following formats:
    - https://steamcommunity.com/profiles/12345678901234567
    - https://steamcommunity.com/id/username

    If the username is not in the correct format, it will
    raise a ValueError.

    Args:
        - username (str): The username to check.

    Returns:
        - str: The correct URL for the user profile.
    """

    if not username.startswith(BASE):
        username = urljoin(BASE, username)

    # Parse the URL and check the path
    parsedUrl = urlparse(username)

    # Get the parts of the path after the BASE URL
    pathParts = parsedUrl.path.strip("/").split("/")

    if len(pathParts) != 2:
        raise ValueError(
            f"Invalid username format. Expected {BASE} followed by two sections. Got {parsedUrl.path}"
        )

    if pathParts[0] == "profiles":
        # Need to make sure the ID is 17 digits long
        if len(pathParts[1]) != 17:
            raise ValueError(
                f"Invalid Steam ID. Expected 17 digits. Got {pathParts[1]}"
            )
        elif not pathParts[1].isdigit():
            raise ValueError(
                f"Invalid Steam ID. Expected 17 digits. Got {pathParts[1]}"
            )

    elif pathParts[0] == "id":
        # Need to make sure the username is not empty
        if not pathParts[1]:
            raise ValueError(
                f"Invalid username. Expected a non-empty string. Got {pathParts[1]}"
            )

    else:
        # If the path is not "profiles" or "id", raise an error
        raise ValueError(
            f"Invalid username format. Expected {BASE} followed by 'profiles' or 'id'. Got {pathParts[0]}"
        )

    # If the URL is correct, return it

    # We return the url with the / at the end
    return f"{username.strip("/")}/"


def getFriends(username: str) -> List[str]:
    """
    Get the list of friends for a Steam user.

    It will return them in the format:
        - https://steamcommunity.com/profiles/12345678901234567

    It gets the following friends:
        - selectable friend_block_v2 persona in-game
        - selectable friend_block_v2 persona online
        - selectable friend_block_v2 persona offline

    Args:
        - username (str): The username to check.

    Returns:
        - List[str]: The list of URLs for the friends' profiles.
    """
    global NORMALCALLS
    url = getCorrectPersonURL(username)

    response = requests.get(urljoin(url, "friends/"))
    NORMALCALLS += 1
    soup = BeautifulSoup(response.text, "html.parser")

    friendClasses = re.compile(r"\bfriend_block_v2\b")

    # Find all elements containing friends' Steam IDs
    friend_blocks = soup.find_all(
        "div",
        class_=friendClasses,
    )

    # Extract Steam IDs
    steam_ids = [
        urljoin(BASE, f"profiles/{block.get("data-steamid")}")
        for block in friend_blocks
        if block.get("data-steamid")
    ]

    return steam_ids


def getName(username: str) -> str:
    """
    Get the name that a Steam user
    has set in their profile.

    Args:
        - username (str): The username to check.

    Returns:
        - str: The name of the user.
    """
    url = getCorrectPersonURL(username)
    global NORMALCALLS

    response = requests.get(url)
    NORMALCALLS += 1
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.find("span", class_="actual_persona_name").text

    return name
