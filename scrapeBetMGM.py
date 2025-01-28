from playwright.sync_api import sync_playwright, expect
import re
import datetime as dt
import time

#TODO: work on fixing the live maybe? not sure how it works with live games


def get_date( date):
    if "Tomorrow" in date:
    #might need to bring back
    # tomorrow = dt.datetime.now() + dt.timedelta(days=1)
        date = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%b %#d, %Y")
    elif "Today" in date:
        date = dt.datetime.now().strftime("%b %#d, %Y")
    else:
        #needs because sometimes the • doesnt load 
        if "•" in date:
            parsed_date = dt.datetime.strptime(date, '%m/%d/%y • %I:%M %p')
        else:
            parsed_date = dt.datetime.strptime(date, '%m/%d/%y %I:%M %p')
        date = parsed_date.strftime("%b %#d, %Y")

    return date


def get_sports(page):
    sports = {} 
    #get left widget items
    top_widget = page.locator("#sports-nav a")
    try:
        try:
            popup = page.locator('svg[title="theme-ex"]')
            popup.wait_for(state='visible', timeout=4000)
            if popup.is_visible():
                popup.click()
        except Exception as e:
            pass
        
        sports["NFL"] = top_widget.locator(":text-is('NFL')")
        sports["NBA"] = top_widget.locator(":text-is('NBA')")
        # sports["NCAAM"] = top_widget.locator(":text-is('NCAAM')")    
        # sports["NHL"] = top_widget.locator(":text-is('NHL')")
    
    except Exception as e:
        print("Error getting  sports:", e)

    return sports

#TODO: check when theres a +100, if it says that or just says even
def get_odds_for_single_team(team_name, spread, total, moneyline):

    #get team info
    team_info = {}
    team_info["team"] = team_name.text_content()

    #get spread odds
    spread_odds = spread.text_content()
    matches = re.findall(r"[+-]?\d+\.\d+|[+-]?\d+", spread_odds)
    team_info["spread"] = {"value": matches[0], "odds": matches[1] }

    #get over/under odds
    total_odds = total.text_content()
    over_under = "over" if "O" in total_odds else "under"
    matches = re.findall(r"-?\d+\.\d+|-?\d+", total_odds)
    team_info[over_under] = {"value": matches[0], "odds": matches[1]}

    #might need to edit later, not sure what they do in case of tie
    team_info["moneyline"] = moneyline.text_content()
    return team_info

def get_odds_for_single_game(page, game):
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
        #get date text and format
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
    return game_odds

def get_odds(page, sports, p):
    odds = {}
    for (sport, button) in sports.items():

        games = []
        button.click()
        # page.pause()
        try:
            #grid with games
            page.wait_for_selector("ms-event-group", timeout=4000)
            game_grid = page.locator("ms-event-group")
            game_list = game_grid.locator("ms-six-pack-event")
            game_count = game_list.count()
            for i in range(game_count):
                games.append(get_odds_for_single_game(page, game_list.nth(i)))
            odds[sport] = games    
        except Exception as e:
            print("Most likely no games found", e)
        
    
    return odds

def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)  
        context = browser.new_context(permissions=[])
        page = context.new_page()
        
        # Navigate to the target URL
        page.goto("https://sports.az.betmgm.com/en/sports")
        

        sports = get_sports(page)
        odds =  get_odds(page, sports, p)
        print(odds)
        browser.close()
        p.stop()

if __name__ == "__main__":
    main()
