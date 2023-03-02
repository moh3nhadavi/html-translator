import glob
import os
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def translate_html_file(filename, target_language, browser):
    # read global dictionary
    global my_dictionary

    # read the html file
    with open(filename, 'r') as file:
        html = file.read()
    soup = BeautifulSoup(html, 'html.parser')

    # skip comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # loop on elements of html
    for element in soup.find_all():

        # skip these elements
        if element.name in ['html', 'style', 'script', 'noscript', 'meta', 'link', 'head', 'body']:
            continue

        # Get the text of the element
        element_text = ""

        # Loop through the contents of the element
        for content in element.contents:

            # If the content is a string, add it to the element text
            if isinstance(content, str):
                element_text += content.strip()
        # Skip empty elements and comments
        if not element_text:
            continue

        # check the element text. if it is already translated, read from dictionary.
        # Else, translate it using Google Translate.
        if element_text in my_dictionary:
            output1 = my_dictionary[element_text]
        else:
            browser.get(
                "https://translate.google.co.in/?sl=auto&tl=" + target_language + "&text=" + element_text + "&op=translate")
            wait = WebDriverWait(browser, 120)
            translate_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "HwtZe")))
            output1 = translate_element.text
            # add to dictionary
            my_dictionary.update({element_text: output1})

        # replace translated text to origin text
        element.string = output1

    # write translated file
    with open(filename, 'w') as file:
        file.write(str(soup))


def replace_text_in_directory(directory_path, target_language):
    # a simple text to just open the Google Translate.
    source_text = "Hello World!"
    browser = webdriver.Chrome()
    browser.get(
        "https://translate.google.co.in/?sl=auto&tl=" + target_language + "&text=" + source_text + "&op=translate")

    # first of all we should press the accept button
    browser.find_elements(By.CLASS_NAME, "nCP5yc")[3].click()

    # wait 60 seconds to get the translated text.
    wait = WebDriverWait(browser, 60)
    translate_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "HwtZe")))

    # browse the files inside the folder and all the subdirectories one by one.
    for root, subdirs, files in os.walk(directory_path):
        for file_path in glob.glob(os.path.join(root, '*.html')):
            print(file_path)
            translate_html_file(file_path, target_language, browser)


directory = 'Path/to/the/directory'
target_language = 'hi'
my_dictionary = {}
replace_text_in_directory(directory, target_language)
