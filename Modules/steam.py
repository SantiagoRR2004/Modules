from urllib.parse import urljoin, urlparse
from typing import List
import requests
from bs4 import BeautifulSoup
import re

BASE = "https://steamcommunity.com/"
COLOR = "#2a475e"
COLOR_GAMES = "#2e5e47"

NORMALCALLS = 0
APICALLS = 0


def resolveVanityURL(url: str, APIKEY: str) -> str:
    """
    Resolve a Steam vanity URL to a SteamID64.

    It doesn't do any calls if it is already a valid SteamID64.

    Args:
        - url (str): The custom Steam profile name.
        - APIKEY (str): The Steam API key to use for the request.

    Returns:
        - str: The SteamID64 or None if not found.
    """
    global APICALLS
    parsedUrl = urlparse(url)

    finalPart = parsedUrl.path.strip("/").split("/")[-1]

    if finalPart.isdigit() and len(finalPart) == 17:
        # If the final part is already a valid SteamID64, return it
        return finalPart

    endpoint = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
    params = {
        "key": APIKEY,
        "vanityurl": finalPart,
    }

    response = requests.get(endpoint, params=params)
    APICALLS += 1
    data = response.json()

    if data["response"]["success"] == 1:
        return data["response"]["steamid"]
    else:
        return None


def validIDURL(url: str) -> bool:
    """
    Check if a URL is a valid Steam ID URL.

    Args:
        - url (str): The URL to check.

    Returns:
        - bool: True if the URL is valid, False otherwise.
    """
    parsedUrl = urlparse(url)

    # Get the parts of the path after the BASE URL
    pathParts = parsedUrl.path.strip("/").split("/")

    if len(pathParts) != 2:
        return False

    if pathParts[0] == "profiles":
        # Need to make sure the ID is 17 digits long
        if len(pathParts[1]) != 17 or not pathParts[1].isdigit():
            return False

        return True

    return False


def validVanityURL(url: str) -> bool:
    """
    Check if a URL is a valid Steam vanity URL.

    Args:
        - url (str): The URL to check.

    Returns:
        - bool: True if the URL is valid, False otherwise.
    """
    # Parse the URL and check the path
    parsedUrl = urlparse(url)

    # Get the parts of the path after the BASE URL
    pathParts = parsedUrl.path.strip("/").split("/")

    if len(pathParts) != 2:
        return False

    if pathParts[0] == "id":
        # Need to make sure the username is not empty
        if not pathParts[1]:
            return False

        return True

    return False


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


def getFriends(username: str, APIKEY: str = None) -> List[str]:
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
        - APIKEY (str): The Steam API key to use for the request.

    Returns:
        - List[str]: The list of URLs for the friends' profiles.
    """
    global NORMALCALLS
    global APICALLS
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

    if steam_ids or not APIKEY:
        # We have found friends, return the list
        return steam_ids

    # Use the API to get friends if no friends were found
    steamid = resolveVanityURL(url, APIKEY)
    endpoint = "https://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
    params = {
        "key": APIKEY,
        "steamid": steamid,
        "relationship": "friend",
        "format": "json",
    }

    response = requests.get(endpoint, params=params)
    APICALLS += 1

    if response.status_code == 401:
        """
        This means the list is not public.
        We will return an empty list.
        """
        return []

    response.raise_for_status()
    data = response.json()

    friends = data.get("friends", [])
    for friend in friends:
        steam_ids.append(urljoin(BASE, f"profiles/{friend['steamid']}"))

    return steam_ids


def getName(username: str, APIKEY: str = None) -> str:
    """
    Get the name that a Steam user
    has set in their profile.

    Args:
        - username (str): The username to check.
        - APIKEY (str): The Steam API key to use for the request.

    Returns:
        - str: The name of the user.
    """
    global NORMALCALLS
    global APICALLS

    url = getCorrectPersonURL(username)

    # If it is already the name, return it
    if validVanityURL(url):
        return url.strip("/").split("/")[-1]

    # Try to get the name from the HTML
    response = requests.get(url)
    NORMALCALLS += 1
    if response.status_code != 429:
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find("span", class_="actual_persona_name").text

        return name

    # If it fails, try to get it from the API
    steamid = resolveVanityURL(url)
    if not steamid:
        raise ValueError("Could not resolve vanity URL")

    endpoint = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": APIKEY, "steamids": steamid}

    response = requests.get(endpoint, params=params)
    APICALLS += 1
    data = response.json()

    players = data["response"]["players"]
    if not players:
        raise ValueError("No user found")

    return players[0]["personaname"]


def getGames(username: str, APIKEY: str) -> List[str]:
    """
    Get the list of games for a Steam user.

    It will return them in the format:
        - https://steamcommunity.com/profiles/12345678901234567

    Args:
        - username (str): The username to check.
        - APIKEY (str): The Steam API key to use for the request.

    Returns:
        - List[str]: The list of game names owned by the user.
            Free games are included if he has played them.
    """
    global APICALLS
    url = getCorrectPersonURL(username)

    steamid = resolveVanityURL(url)

    endpoint = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": APIKEY,
        "steamid": steamid,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json",
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    APICALLS += 1
    data = response.json()

    games = data.get("response", {}).get("games", [])
    return [g["name"] for g in games]
