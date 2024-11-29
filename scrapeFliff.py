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
        sports_scrollbar = WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".channels-list-wrapper__inner.no-scroll-bars")))
    except:
        print("header not found")
    try:
        sports.extend(WebDriverWait(sports_scrollbar, 10).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-basketball"))))
    except:
        print("basketball not found")
    try:
        sports.extend(WebDriverWait(sports_scrollbar, 10).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-nflball"))))
    except:
        print("football not found")
    try:
        sports.extend(WebDriverWait(sports_scrollbar, 10).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, ".icon.icon-nhlball"))))
    except:
        print("nhl not found")
    return sports


def get_odds_for_single_team(driver,team):
    team_info = {}
    team_info["team"] = team.find_element(By.CSS_SELECTOR, ".card-row-header").text
    team_odds = team.find_elements(By.CSS_SELECTOR, ".card-cell-wrapper")
    for card in team_odds:
            values = card.find_elements(By.TAG_NAME, "span")
            #if theres a number and odd value (spread, total)
            if len(values) == 2:
                value = card.find_element(By.CSS_SELECTOR, ".card-cell-param-label").text
                odd = card.find_element(By.CSS_SELECTOR, ".card-cell-label").text
                #we found over
                if "O" in value :
                    team_info["over"] =  {"value" : value, "odds": odd}
                #we found under
                elif "U" in value:
                    team_info["under"] =  {"value" : value, "odds": odd}
                #spread
                else:    
                    team_info["spread"] = {"value" : value, "odds": odd}

            else:
                #didnt find the extra text, so its moneyline
                team_info["moneyline_odds"] = card.text
    return team_info

def get_odds_for_single_game(driver, gameElement):

        game = {}
        #get teams
        game_info = WebDriverWait(gameElement, 10).until(
            expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR,".double-grid-card__group"))
            )
        #get home team info
        game["home"] = get_odds_for_single_team(driver, game_info[0])
        game["away"] = get_odds_for_single_team(driver, game_info[1])
        return game

def get_odds(driver, sports):
    odds = {}
    #loop through sports ie, NFL, NBA, NHL
    for idx,sport in enumerate(sports):
        try:
            sport.click()
        except Exception as e:
            print(e)
            print(idx)
        games_in_division = []
        #name of division
        try:
            division = WebDriverWait(driver, 4).until(
                expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,".card-bottom-left-info__name"))
                ).text
        except TimeoutException:
            print("error getting games")
            continue
        games = WebDriverWait(driver, 10).until(
             expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR,".card-shared-container"))
             )
        #for game in games:
        print("num of games found", len(games))
        for game in games:
            games_in_division.append(get_odds_for_single_game(driver, game))
        odds[division] = games_in_division

    return odds


def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
    driver = webdriver.Chrome(options=options)
    driver.get("https://sports.getfliff.com")
    sports = get_sports(driver)
    odds = get_odds(driver, sports)
    print(odds)
    driver.close()


if __name__ == "__main__":
    main()