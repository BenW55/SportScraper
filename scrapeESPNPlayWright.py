#TODO: work on fixing the live

from playwright.sync_api import sync_playwright
import re
import datetime as dt
def get_sports(page):
    base_url = "https://espnbet.com"
    sports = {}
    try:
        sports_element = page.get_by_test_id("chip-NFL").get_attribute("href")
        sports["NFL"] = base_url+sports_element
        sports_element = page.get_by_test_id("chip-NCAAF").get_attribute("href")
        sports["NCAAF"] = base_url+sports_element
        sports_element = page.get_by_test_id("chip-NCAAB").get_attribute("href")
        sports["NCAAB"] = base_url+sports_element
        sports_element = page.get_by_test_id("chip-NBA").get_attribute("href")
        sports["NBA"] = base_url+sports_element
        sports_element = page.get_by_test_id("chip-NHL").get_attribute("href")
        sports["NHL"] = base_url+sports_element
        sports_element = page.get_by_test_id("chip-WNCAAB").get_attribute("href")
        sports["WNCAAB"] = base_url+sports_element
    
    except Exception as e:
        print("Error getting  sports:", e)

    return sports

def get_odds_for_single_team(team):
    
    team_info = {}
    team_info["team"] = team.locator(".text-style-s-medium.text-primary.text-primary").text_content()
    odds = team.get_by_test_id("Add Bet Selections")
    num_odds = odds.count()
    for i in range(num_odds):
        odds_text = odds.nth(i).text_content()
        #if its over
        if "O" in odds_text:
            #get the matches for value and odds
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["over"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        #if its under
        elif "U" in odds_text:
            #get the matches for value and odds
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["under"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        #if its spread
        elif "." in odds_text:
            #get the matches for value and odds
            matches = re.findall(r"[+-]?\d+\.\d+|[+-]?\d+", odds_text)
            team_info["spread"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        else:
            team_info["moneyline"] = "+100" if odds_text == "Even" else odds_text 
    return team_info
def get_odds_for_single_game(game):
    game_odds = {}
    
    try:
        #teams name and betting info
        team_info = game.locator('.flex.p-0')
        #get date and edit it
        date = game.locator('.text-style-xs-medium.flex.items-center.gap-x-2').text_content()
        date = " ".join(date.split(" ")[:3])
        if "Today" in date:
            date = dt.datetime.now().strftime("%b %#d, %Y")
        game_odds["date"] = date

        game_odds["away"] = get_odds_for_single_team(team_info.nth(0))
        game_odds["home"] = get_odds_for_single_team(team_info.nth(1))
        #if we dont have away yet just make over None and if we dont have over in away just set to None
        game_odds["over"] = game_odds.get("away", {}).get("over", None)

        #remove over from the away dict
        game_odds.get("away").pop("over", "none found")

        #if we dont have ynder yet just make under none and if we dont have over in away just set to None
        game_odds["under"] = game_odds.get("home").get("under", None)

        #remove under from the home dict
        game_odds.get("home").pop("under", "none found")
    except Exception as e:
        print("error getting odds for single game", e)
        print(game.text_content())
    return game_odds

def get_odds(page, sports, p):
    odds = {}
    for sport,url in sports.items():
        games = []
        page.goto(url)
        try:
            #get game grid
            game_grid = page.get_by_test_id("marketplace-shelf-")
            #get all of the games into a list
            game_list = game_grid.get_by_role("article") 
            page.wait_for_selector('article')
            game_count = game_list.count()
            for i in range(game_count):
                #adjusting test id attribute to data-dd-action-name
                p.selectors.set_test_id_attribute("data-dd-action-name")
                #get info for a single game
                games.append(get_odds_for_single_game(game_list.nth(i)))
                #reset test id attribute 
                p.selectors.set_test_id_attribute("data-testid")
            odds[sport] = games    
        except Exception as e:
            print("Most likely no games found", e)
        
    
    return odds

def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()
        
        # Navigate to the target URL
        page.goto("https://espnbet.com")
        

        sports = get_sports(page)
        odds =  get_odds(page, sports, p)
        print(odds)
        browser.close()
        p.stop()

if __name__ == "__main__":
    main()
