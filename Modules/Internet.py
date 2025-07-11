import requests
from Modules import FileHandling
from Modules import zipping
import os
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import secretstorage
import sys


def downloadImage(url, dest_file):
    if not os.path.isfile(dest_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(dest_file, "wb") as f:
                f.write(response.content)
        time.sleep(random.uniform(0.1, 1))


def mangasee123UrlsXML(web):
    r = requests.get(web)
    page = BeautifulSoup(r.content, "xml")
    urls = [item.find("link").text for item in page.find_all("item")]
    return urls[::-1]


def configureChrome() -> webdriver.Chrome:
    """
    Configures a Chrome WebDriver instance
    and tries to say it is not automated

    Returns:
        webdriver.Chrome: A WebDriver instance
    """
    # pip install --upgrade selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # userDataDir = os.path.join(os.path.expanduser("~"), ".config", "google-chrome", "Default")
    # chrome_options.add_argument(f"user-data-dir={userDataDir}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(options=chrome_options, service=service)


def clickButton(driver, name):
    wait = WebDriverWait(
        driver, 10
    )  # Wait up to 10 seconds for the button to be clickable
    button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., '" + name + "')]"))
    )
    button.click()


def findPNGs(driver):
    script = """
var mainContainerElements = document.getElementsByClassName('MainContainer');
var images = [];
for (var i = 0; i < mainContainerElements.length; i++) {
  var container = mainContainerElements[i];
  var imgElements = container.getElementsByTagName('img');
  for (var j = 0; j < imgElements.length; j++) {
    images.push(imgElements[j]);
  }
}
return images;
"""
    image_elements = driver.execute_script(script)
    png_image_urls = []

    # Loop through each image element and extract the source URL if it's a PNG image
    for img_element in image_elements:
        src = img_element.get_attribute("src")
        if src and src.lower().endswith(".png"):
            png_image_urls.append(src)

    remove = ["https://bidgear.com/images/close-icon.png"]
    png_image_urls = [url for url in png_image_urls if url not in remove]

    return sorted(list(set(png_image_urls)))


def mangasee123Downloader(
    manga, chapter, maxDownload, callerDirectory, skip=[], missing=[]
):
    mangaSpaces = manga.replace(" ", "")
    mangaHyphens = manga.replace(" ", "-")

    infofile = os.path.join(callerDirectory, "Manga.json")
    mangaData = FileHandling.openJson(infofile)

    if mangaData.get(mangaSpaces):
        if mangaData.get(mangaHyphens).get("skip"):
            skip = mangaData[mangaHyphens]["skip"]
        if mangaData.get(mangaHyphens).get("missing"):
            missing = mangaData[mangaHyphens]["missing"]

    web = "https://mangasee123.com/rss/" + mangaHyphens + ".xml"
    folder = os.path.join(callerDirectory, "." + mangaSpaces + "JPG")
    urls = mangasee123UrlsXML(web)

    for x in skip:
        if x in urls:
            urls.remove(x)

    for x in missing:
        urls.insert(x - 1, "missing")

    if len(urls) < maxDownload:
        print("There aren't that many chapters")
        maxDownload = len(urls)

    if len(urls) < chapter:
        print("The starting chapter is too high")
        chapter = len(urls)

    if chapter < 1:
        print("The starting chapter can't be less than 1")
        chapter = 1

    if maxDownload < 1:
        print("The last chapter can't be less than 1")
        maxDownload = 1

    FileHandling.ensureExistance(folder)
    driver = configureChrome()

    while chapter <= maxDownload:
        if chapter in missing:
            pass

        else:
            driver.get(urls[chapter - 1])
            clickButton(driver, "Long Strip")

            png_image_urls = findPNGs(driver)

            for i in range(len(png_image_urls)):
                name = (
                    str(chapter) + "{:0>{}}".format(i, 3) + ".jpg"
                )  # Try to change it to png
                downloadImage(png_image_urls[i], os.path.join(folder, name))

        print("Se ha descargado el capítulo " + str(chapter))
        chapter += 1
        time.sleep(random.uniform(1, 10))

    driver.quit()

    zipping.zipAndDelete(folder)


def getCookies() -> list:
    """
    Returns a list with the cookies from the Chrome browser.

    It returns a list of dictionaries. Each dictionary
    contains the columns of the cookies table as keys
    and the values of the columns as values.
    """

    userHome = os.path.expanduser("~")
    cookiesPath = os.path.join(
        userHome, ".config", "google-chrome", "Default", "Cookies"
    )

    conn = sqlite3.connect(cookiesPath)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(cookies);")

    columnNames = [column[1] for column in cursor.fetchall()]

    cursor.execute(f"SELECT {", ".join(columnNames)} FROM cookies;")
    unformattedData = cursor.fetchall()
    conn.close()
    data = []

    for row in unformattedData:
        data.append(dict(zip(columnNames, row)))

    return data


def clean(x: bytes) -> str:
    """
    Removes the padding from the decrypted value.

    Args:
        x (bytes): The decrypted value.

    Returns:
        str: The decrypted value without padding.
    """
    try:
        return x[: -x[-1]].decode("utf8")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        # Optionally, handle the error as needed
        # For example, you can ignore errors or replace them:
        return x[: -x[-1]].decode("utf8", errors="replace")


def decryptCookies(cookies: list) -> list:
    """
    Decrypts the cookies from the Chrome browser.
    https://stackoverflow.com/questions/23153159/decrypting-chromium-cookies/23727331#23727331

    Args:
        cookies (list): A list containing the cookies (each a dict).
                    The key is the name of the column and the value is the value of the column.

    Returns:
        dict: A list containing the decrypted cookies (each a dict).
                    The encrypted value key is replaced by value
    """
    bus = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(bus)
    for item in collection.get_all_items():
        if item.get_label() == "Chrome Safe Storage":
            MY_PASS = item.get_secret()
            break
    else:
        raise Exception("Chrome password not found!")

    decryptedCookies = []

    for cookie in cookies:
        # Trim off the 'v10' that Chrome/ium prepends
        encrypted_value = cookie["encrypted_value"][3:]

        if encrypted_value:

            # Default values used by both Chrome and Chromium in OSX and Linux
            salt = b"saltysalt"
            iv = b" " * 16
            length = 16

            # 1003 on Mac, 1 on Linux
            iterations = 1
            if sys.platform.startswith("linux"):
                iterations = 1
            elif sys.platform.startswith("darwin"):
                iterations = 1003

            key = PBKDF2(MY_PASS, salt, length, iterations)
            cipher = AES.new(key, AES.MODE_CBC, IV=iv)

            decrypted = cipher.decrypt(encrypted_value)
            del cookie["encrypted_value"]
            cookie["value"] = clean(decrypted)
            decryptedCookies.append(cookie)

    return decryptedCookies
