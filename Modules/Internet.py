import requests
import os
import random
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

   
def downloadImage(url, dest_file):
    if not os.path.isfile(dest_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(dest_file, 'wb') as f:
                f.write(response.content)
        time.sleep(random.uniform(0.1, 1))

def configureChrome():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/opt/google/chrome/google-chrome"
    return webdriver.Chrome(options=chrome_options)

def clickButton(driver,name):
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for the button to be clickable
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '"+name+"')]")))
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
        src = img_element.get_attribute('src')
        if src and src.lower().endswith('.png'):
            png_image_urls.append(src)

    return sorted(list(set(png_image_urls)))
