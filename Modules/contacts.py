import pandas as pd
import re


def deleteEmptyColumns(data: dict) -> dict:
    """
    Get rid of columns that are all empty.

    It can also recieve a DataFrame,
    but it will return a dictionary.

    Args:
        - data (dict): The data to filter

    Returns:
        dict: The filtered data
    """

    # To not increase overhead
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Filter out columns where all values are either NaN or empty strings
    data = data.loc[:, ~(data.isna() | (data == "")).all()]

    return data.to_dict(orient="list")


def findWebsite(data: dict, website: str) -> dict:
    """
    Find the people with a type website
    and only returns those. It also
    eliminates empty columns.

    It can also recieve a DataFrame,
    but it will return a dictionary.

    Args:
        - data (dict): The data to filter
        - website (str): The website to find

    Returns:
        - dict: The filtered data
    """

    # To not increase overhead
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Regular expression pattern to match "Website <number> - Label"
    pattern = re.compile(r"^Website \d+ - Label$")

    columns = [col for col in data.columns if pattern.match(col)]

    # Filter rows where any matching column contains the website no matter the case
    filteredRows = data[
        data[columns].apply(
            lambda row: row.str.contains(website, case=False, na=False).any(), axis=1
        )
    ]

    return deleteEmptyColumns(filteredRows)


def urlWithNames(pathToCsv: str, websiteLabel: str) -> dict:
    """
    Get the people with a website and their names.

    Args:
        - pathToCsv (str): The path to the CSV file
        - websiteLabel (str): The label of the website

    Returns:
        - dict: The people with the website and their names.
                The keys are the websites and the values are the names.
    """
    data = pd.read_csv(pathToCsv)

    # We replace NaN with None
    data = data.where(pd.notnull(data), None)

    # We filter the data to only have the people with the website
    data = findWebsite(data, websiteLabel)

    if not data:
        print(f"No people with {websiteLabel}")
        return {}

    nPeople = len(list(data.values())[0])

    print(f"Number of people with {websiteLabel}: {nPeople}")

    # Only one person per account
    usersWithWebsite = {}

    for i in range(nPeople):
        name = " ".join(
            part
            for part in [
                data["First Name"][i] if data.get("First Name") else "",
                data["Middle Name"][i] if data.get("Middle Name") else "",
                data["Last Name"][i] if data.get("Last Name") else "",
            ]
            if part
        )

        found = False
        j = 1
        while not found:
            if websiteLabel.lower() in data[f"Website {j} - Label"][i].lower():
                for g in data[f"Website {j} - Value"][i].split(" ::: "):
                    usersWithWebsite[g] = name
                found = True
            j += 1

    return usersWithWebsite


def uniqueWebsites(pathToCsv: str) -> list:
    """
    Get the unique websites in a CSV file.

    Args:
        - pathToCsv (str): The path to the CSV file

    Returns:
        - list: The unique websites
    """
    data = pd.read_csv(pathToCsv)

    # We replace NaN with None
    data = data.where(pd.notnull(data), None)

    # Regular expression pattern to match "Website <number> - Label"
    pattern = re.compile(r"^Website \d+ - Label$")

    columns = data.filter(regex=pattern)

    websites = set(columns.stack().explode().dropna())

    return sorted(list(websites))
