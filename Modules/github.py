import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://github.com"


def getCorrectURL(username):
    if not username.startswith(BASE):
        return urljoin(BASE, username)
    return username


def getFollowers(username):

    web = getCorrectURL(username)

    return getConnection(f"{web}?tab=followers")


def getFollowing(username):

    web = getCorrectURL(username)

    return getConnection(f"{web}?tab=following")


def getConnection(url):
    # Initialize an empty list to store the URLs of each
    people = []

    while url:

        response = requests.get(url)
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
