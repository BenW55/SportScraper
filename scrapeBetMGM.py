from playwright.sync_api import sync_playwright, expect
import re
import datetime as dt
import time
def get_sports(page):
    sports = {} 
    #get left widget items
    top_widget = page.locator("#sports-nav a")
    top_widget_count = top_widget.count()
    try:
        
        popup = page.locator('svg[title="theme-ex"]')
        popup.wait_for(state='visible', timeout=10000)

        if popup.is_visible():
            popup.click()
        sports["NFL"] = top_widget.locator("text=NFL")
        sports["NBA"] = top_widget.locator("text=NBA", exact=True)   
        sports["NCAAB"] = top_widget.locator("text=NCAAB")    
        sports["NHL"] = top_widget.locator("text=NHL")
    
        for sport in sports.values():
            sport.click()
            time.sleep(3)
    
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
        if "O" in odds_text:
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["over"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        elif "U" in odds_text:
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["under"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        elif "." in odds_text:
            matches = re.findall(r"[+-]?\d+\.\d+|[+-]?\d+", odds_text)
            team_info["spread"] = {"value": matches[0], "odds": matches[1] if len(matches) > 1 else "+100"}
        else:
            team_info["moneyline"] = "+100" if odds_text == "Even" else odds_text 
    return team_info
def get_odds_for_single_game(game):
    game_odds = {}
    
    try:
        team_info = game.locator('.flex.p-0')
        
        date = game.locator('.text-style-xs-medium.flex.items-center.gap-x-2').text_content()
        date = " ".join(date.split(" ")[:3])
        if "Today" in date:
            date = dt.datetime.now().strftime("%b %#d, %Y")
        game_odds["date"] = date
        game_odds["away"] = get_odds_for_single_team(team_info.nth(0))
        game_odds["home"] = get_odds_for_single_team(team_info.nth(1))
        game_odds["over"] = game_odds.get("away", {}).get("over", None)
        game_odds.get("away").pop("over", "none found")
        game_odds["under"] = game_odds.get("home").get("under", None)
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
            game_grid = page.get_by_test_id("marketplace-shelf-")
            game_list = game_grid.get_by_role("article") 
            page.wait_for_selector('article')
            game_count = game_list.count()
            for i in range(game_count):
                p.selectors.set_test_id_attribute("data-dd-action-name")
                games.append(get_odds_for_single_game(game_list.nth(i)))
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
        page.goto("https://sports.az.betmgm.com/en/sports")
        

        sports = get_sports(page)
        # odds =  get_odds(page, sports, p)
        # print(odds)
        browser.close()
        p.stop()

if __name__ == "__main__":
    main()
