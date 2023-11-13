from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape():
    # Set up the driver for the browser of your choice (e.g., Chrome, Firefox)
    driver = webdriver.Chrome()
    file = open('links.txt', 'w')
    try:
        for i in range(1, 100):
            # Generate the URL for the current page of games
            url = 'https://replay.pokemonshowdown.com/?format=gen9ou&page=' + str(i) + '&sort=rating'
            driver.get(url)
            # Wait for the dynamic element to be present on the page
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'blocklink'))
            )
            # Extract the text from each element
            for element in elements:
                href = element.get_attribute('href')
                print(href)
                file.write(href + "\n")
    finally:
        file.close()
        driver.quit()  # Quit the driver after the loop is finished
