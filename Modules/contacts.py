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
