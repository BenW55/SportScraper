from playwright.sync_api import sync_playwright, expect
import re
import datetime as dt
import time

#TODO: work on fixing the live maybe? not sure how it works with live games


def get_date(date):
    if "Tomorrow" in date:
    #might need to bring back
    # tomorrow = dt.datetime.now() + dt.timedelta(days=1)
        date = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%b %#d, %Y")
    elif "Today" in date:
        date = dt.datetime.now().strftime("%b %#d, %Y")
    else:
        parsed_date = dt.datetime.strptime(date, '%m/%d/%y • %I:%M %p')
        date = parsed_date.strftime("%b %#d, %Y")

    return date


def get_sports(page):
    sports = {} 
    #get left widget items
    top_widget = page.locator("#sports-nav a")
    top_widget_count = top_widget.count()
    try:
        try:
            popup = page.locator('svg[title="theme-ex"]')
            popup.wait_for(state='visible', timeout=6000)
            if popup.is_visible():
                popup.click()
        except Exception as e:
            pass

        sports["NFL"] = top_widget.locator("text=NFL")
        sports["NBA"] = top_widget.locator("text=NBA", exact=True)   
        sports["NCAAB"] = top_widget.locator("text=NCAAB")    
        sports["NHL"] = top_widget.locator("text=NHL")
    
    except Exception as e:
        print("Error getting  sports:", e)

    return sports
#TODO: not updated
def get_odds_for_single_team(team_name, spread, total, moneyline):
    
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
        #get team name
        team_name = game.locator('.participant-container')
        #get container with all odds
        odds_info = game.locator('ms-option-group')
        #get both odds container within the spread container
        spread_info = odds_info.nth(0).locator('ms-option')
        #get both odds container within the total container
        total_info = odds_info.nth(1).locator('ms-option')
        #get both odds container within the moneyline container
        money_info = odds_info.nth(2).locator('ms-option')

        date = get_date(game.locator('ms-event-timer').text_content())

        game_odds["date"] = date
        game_odds["away"] = get_odds_for_single_team(team_name.nth(0), spread_info.nth(0), total_info.nth(0), money_info.nth(0))
        game_odds["home"] = get_odds_for_single_team(team_name.nth(1), spread_info.nth(1), total_info.nth(1), money_info.nth(1))
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
    for sport, button in sports:
        games = []
        button.click()
        try:
            #grid with games
            game_grid = page.locator("ms-event-group")
            #TODO: might cause slight error, six pack might mean all 6 odds(ML spread total) so ones without might be diff
            #get all of the boxes that have represent games
            game_list = game_grid.locator("ms-six-pack-event")
            game_count = game_list.count()
            for i in range(game_count):
                games.append(get_odds_for_single_game(game_list.nth(i)))
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
        odds =  get_odds(page, sports, p)
        # print(odds)
        browser.close()
        p.stop()

if __name__ == "__main__":
    main()
