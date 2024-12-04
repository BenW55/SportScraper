"""
THIS PROGRAM IS PRONE TO BREAKING, THE WEBSITE HAS NO CLEAR WAY TO SCRAPE( EVERYTHING IS A DIV AND CLASES ARE "GC AF S" ETC)
IF IT SUDDENLY STOPS WORKING, CHECK THE CSS ON THE WEBSITE
"""
from playwright.sync_api import sync_playwright
import re
import datetime as dt
import time
def get_sports(page):
    base_url = "https://sportsbook.fanduel.com"
    sports = {}
    try:
        sports_element = page.get_by_title("NFL").first.get_attribute("href")
        sports["NFL"] = base_url+sports_element
        # sports_element = page.get_by_title("NCAAF").first.get_attribute("href")
        # sports["NCAAF"] = base_url+sports_element
        # sports_element = page.get_by_title("NCAAB").first.get_attribute("href")
        # sports["NCAAB"] = base_url+sports_element
        # sports_element = page.get_by_title("NCAAF").first.get_attribute("href")
        # sports["NCAAF"] = base_url+sports_element
        # sports_element = page.get_by_title("NBA").first.get_attribute("href")
        # sports["NBA"] = base_url+sports_element
        # sports_element = page.get_by_title("NHL").first.get_attribute("href")
        # sports["NHL"] = base_url+sports_element
    
    except Exception as e:
        print("Error getting  sports:", e)

    return sports

def get_odds_for_single_team(team, team_odds):
    
    team_info = {}
    # team_info["team"] = team.locator("").text_content()
    print(team_odds.text_content())
    odds = team_odds.get_by_role("div")
    num_odds = odds.count()
    for i in range(num_odds):
        odds_text = odds.nth(i).text_content()
        print(odds_text)
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
    print(team_info)
    return team_info
def get_odds_for_single_game(game):
    game_odds = {}
    
    try:
        team_info = game.locator('.am.an.ao.ap.cp.cy.af.s.h.i.j.ah.ai.m.aj.o.ak.q.al')
        print("team info", team_info.text_content())
        odds_info_away = game.locator(".am.aq.ao.bi.af.ho.s.cj.h.i.j.ah.ai.m.aj.o.ak.q.al")
        odds_info_home = game.locator(".am.aq.ao.bi.af.ho.s.h.i.j.ah.ai.m.aj.o.ak.q.al")
        # TODO: fix date
        # date = game.locator('.text-style-xs-medium.flex.items-center.gap-x-2').text_content()
        # date = " ".join(date.split(" ")[:3])
        # if "Today" in date:
        #     date = dt.datetime.now().strftime("%b %#d, %Y")
        # game_odds["date"] = date
        game_odds["away"] = get_odds_for_single_team(team_info.nth(0), odds_info_away)
        game_odds["home"] = get_odds_for_single_team(team_info.nth(1), odds_info_home)

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

def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()
        
        # Navigate to the target URL
        page.goto("https://sportsbook.fanduel.com")
        sports = get_sports(page)
        odds =  get_odds(page, sports)
        # print(odds)
        # browser.close()

if __name__ == "__main__":
    main()
