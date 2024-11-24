from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def get_games(driver):
    sports = []
    try:
        sports.extend(WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-basketball"))))
    except:
        print("basketball not found")
    try:
        sports.extend(WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-nflball"))))
    except:
        print("football not found")
    try:
        sports.extend(WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-nhlball"))))
    except:
        print("nhl not found")
    return sports

def get_odds(driver, sports):
    odds = {}
    #loop through sports ie, NFL, NBA, NHL
    for sport in sports:
        sport.click()
        games_in_division = []
        #name of division
        division = WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,".card-bottom-left-info__name"))
            ).text
        print(division)
        games = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR,".card-shared-container"))
            )
        for game in games:
            odds_per_game_in_sport = {}
            #get teams
            teams = WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR,".card-team-name.label.card-row-header__team"))
                )
            odds_per_game_in_sport["teams"] = [team.text for team in teams]
            print(odds_per_game_in_sport["teams"])
            #get money line
            
            #get spread

            #get total
        
        odds[division] = games_in_division


def main():
    options = Options()
    mobile_emulation = {
        "deviceName" : "Pixel 2"
    }
    options.add_experimental_option("mobileEmulation" ,mobile_emulation)
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get("https://sports.getfliff.com")
    sports = get_games(driver)
    odds = get_odds(driver, sports)
    # driver.close()


if __name__ == "__main__":
    main()