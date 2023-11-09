from selenium import webdriver

from frontend.gui import GUI
from frontend.driver import WebDriver

def main() -> None:
    gui = GUI('Pokemon Showdown Bot', '500x500')
    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors-spki-list')
    driver = WebDriver(options=options)
    driver.get("https://play.pokemonshowdown.com/")
    
    gui.hook(driver)
    gui.run()
    
    driver.quit()

if __name__ == '__main__':
    main()
