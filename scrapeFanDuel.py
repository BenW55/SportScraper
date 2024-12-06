"""
THIS PROGRAM IS PRONE TO BREAKING, THE WEBSITE HAS NO CLEAR WAY TO SCRAPE( EVERYTHING IS A DIV AND CLASES ARE "GC AF S" ETC)
IF IT SUDDENLY STOPS WORKING, CHECK THE CSS ON THE WEBSITE
IN PYTHON 3.15 get_date will break.
"""
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re
from datetime import datetime, timedelta
import time
def get_sports(page):
    base_url = "https://sportsbook.fanduel.com"
    sports = {}
    try:
        sports_element = page.get_by_title("NFL").first.get_attribute("href")
        sports["NFL"] = base_url+sports_element
        sports_element = page.get_by_title("NCAAF").first.get_attribute("href")
        sports["NCAAF"] = base_url+sports_element
        sports_element = page.get_by_title("NBA").first.get_attribute("href")
        sports["NBA"] = base_url+sports_element
        sports_element = page.get_by_title("NHL").first.get_attribute("href")
        sports["NHL"] = base_url+sports_element
        sports_element = page.get_by_title("NCAAB").first.get_attribute("href")
        sports["NCAAB"] = base_url+sports_element


    
    except Exception as e:
        print("Error getting  sports:", e)

    return sports
def get_date(date_str):
    try:
        if ',' in date_str:  # Format: "Dec 16, 8:31pm ET"
            date = datetime.strptime(date_str, "%b %d, %I:%M%p ET").replace(year=datetime.now().year)
            return date.strftime("%b %#d, %Y")
        elif any(day in date_str for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):  # Format: "Sun 1:00pm ET"
            today = datetime.now()
            target_day = datetime.strptime(date_str.split(' ')[0], "%a").weekday()
            days_ahead = (target_day - today.weekday()) % 7
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%b %#d, %Y")
        else:  # Format: "7:00pm ET" (use today's date)
            today = datetime.now()
            return today.strftime("%b %#d, %Y")
    except Exception as e:
        return f"Error: {e}"
    
def get_odds_for_single_team(team, team_odds):
    
    team_info = {}
    
    team_info["team"] = re.sub("[0-9]*", "", team.text_content())
    odds = team_odds.locator(".am.an.bj.bi.cp.cy.ae.af.cz.hw.db.s.cn.ja.bs.y.jj.jk.bv.jl.h.i.j.ah.ai.m.aj.o.ak.q.al")
    
    num_odds = odds.count()

    for i in range(num_odds):
        odds_text = odds.nth(i).text_content()
        
        # print(odds_text)
        if "O" in odds_text:
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["over"] = {"value": matches[0], "odds": matches[1] }
        elif "U" in odds_text:
            matches = re.findall(r"-?\d+\.\d+|-?\d+", odds_text)
            team_info["under"] = {"value": matches[0], "odds": matches[1] }
        elif odds_text.count("+") + odds_text.count("-") >= 2: 
            matches = re.findall(r"[+-]?\d+\.\d+|[+-]?\d+", odds_text)
            team_info["spread"] = {"value": matches[0], "odds": matches[1] }
        else:
            team_info["moneyline"] =  odds_text 

    # print(team_info)
    return team_info

def get_odds_for_single_game(game):
    game_odds = {}
    
    try:
        # print("\n new game \n")
        team_info = game.locator(".am.an.ao.ap.cp.cy.af.s.h.i.j.ah.ai.m.aj.o.ak.q.al").all()
        odds_info = game.locator(".am.aq.ao.bi.af.ho.s.h.i.j.ah.ai.m.aj.o.ak.q.al").all()
        # print(len(team_info))
        # print("away odds", odds_info[0].text_content())

        # print("home odds", odds_info[1].text_content())
        date_info = game.get_by_role("time").text_content()
        game_odds["date"] = get_date(date_info)

        game_odds["away"] = get_odds_for_single_team(team_info[0], odds_info[0])
        game_odds["home"] = get_odds_for_single_team(team_info[2], odds_info[1])

        game_odds["over"] = game_odds.get("away", {}).get("over", None)
        game_odds.get("away").pop("over", "none found")
        game_odds["under"] = game_odds.get("home").get("under", None)
        game_odds.get("home").pop("under", "none found")
    except Exception as e:
        print("error getting odds for single game", e)
        print(game.text_content())
    return game_odds

def get_odds(page, sports):
    odds = {}
    for sport,url in sports.items():
        games = []
        page.goto(url)
        time.sleep(2)
        try:
            game_grid = page.locator(".hx.af.s.h.i.j.ah.ai.m.aj.o.ak.q.al")
            game_list = game_grid.locator(".am.an.ao.ap.cp.cy.af.ar.s.cl.hl.hm.bs.h.i.j.ah.ai.m.aj.o.ak.q.al") 
            game_count = game_list.count()
            for i in range(game_count):
                games.append(get_odds_for_single_game(game_list.nth(i)))
            # TODO: fix WNCAAB
            odds[sport] = games    
        except Exception as e:
            print("Most likely no games found", e)
        
    
    return odds

def human_like_context(context):
    context.add_init_script("""
        // Overwrite the navigator.webdriver property to avoid detection
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)

def main():
    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)  
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},  # Common screen size
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
            human_like_context(context)
            page = context.new_page()
            # Navigate to the target URL
            page.set_default_navigation_timeout(40000)
            page.goto("https://sportsbook.fanduel.com")
            
            sports = get_sports(page)
            time.sleep(2)
            odds =  get_odds(page, sports)
            print(odds)
            browser.close()
            p.stop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
