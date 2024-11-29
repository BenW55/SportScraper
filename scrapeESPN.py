from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

def get_sports(driver):
    sports = []
    try:
        # sports.extend(driver.find_elements(By.XPATH,"//a[@data-testid]"))
        WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//a[contains(@data-testid, 'chip-NFL')]"))
        )
    except Exception as e:
        print("error getting nfl", e)
    for sport in sports:
        print(sport.get_attribute('href'))
    print(len(sports))


def main():
    options = Options()
    options.add_experimental_option("detach", True)
    # options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
    driver = webdriver.Chrome(options=options)
    driver.get("https://espnbet.com/?%243p=a_espn&utm_source=ESPN&utm_campaign=espn-web_global-navigation_espn-bet_sportsbook_install_all_web_app_espn-navigation&utm_medium=paid%20advertising")
    sports = get_sports(driver)
    # odds = get_odds(driver, sports)
    # print(odds)
    # driver.close()


if __name__ == "__main__":
    main()