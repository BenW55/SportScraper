#TODO: work on fixing the live

from playwright.sync_api import sync_playwright
import datetime as dt

def get_games(page):
    sports = []
    try:
        sports_scrollbar = page.wait_for_selector(".channels-list-wrapper__inner.no-scroll-bars", timeout=10000)
        sports.extend(sports_scrollbar.query_selector_all(".icon.icon-basketball"))
        sports.extend(sports_scrollbar.query_selector_all(".icon.icon-nflball"))
        sports.extend(sports_scrollbar.query_selector_all(".icon.icon-nhlball"))
    except Exception as e:
        print(f"Error fetching games: {e}")
    return sports


def get_odds_for_single_team(team):
    team_info = {}
    try:
        team_info["team"] = team.locator(".card-row-header").text_content()
        team_odds = team.locator(".card-cell-wrapper")
        team_odds_length =team_odds.count()
        # for card in team_odds:
        for i in range(team_odds_length):
            values = team_odds.nth(i).locator("span")
            if values.count() == 2:  # If there's a number and odds value (spread, total)
                value = values.nth(0).text_content()
                odd = values.nth(1).text_content()

                if "O" in value:  # Found over
                    team_info["over"] = {"value": value, "odds": odd}
                elif "U" in value:  # Found under
                    team_info["under"] = {"value": value, "odds": odd}
                else:  # Spread
                    team_info["spread"] = {"value": value, "odds": odd}
            else:
                team_info["moneyline_odds"] = team_odds.nth(i).text_content()
    except Exception as e:
        print(f"Error fetching odds for single team: {e}")
    return team_info


def get_odds_for_single_game(page, game_element):
    game_info = {}
    try:
        teams = game_element.locator(".double-grid-card__group")
        date = game_element.locator(".card-top-left-info").text_content()
        date = " ".join(date.split(" ")[:-2])
        if "Today" in date:
            date = dt.datetime.now().strftime("%b %#d, %Y")
        elif "Tomorrow" in date:
            date = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%b %#d, %Y")
        game_info["date"] = date
        
        game_info["away"] = get_odds_for_single_team(teams.nth(0))
        game_info["home"] = get_odds_for_single_team(teams.nth(1))
        game_info["over"] = game_info.get("away", {}).get("over", None)
        game_info.get("away").pop("over", "none found")
        game_info["under"] = game_info.get("home").get("under", None)
        game_info.get("home").pop("under", "none found")
    except Exception as e:
        print(f"Error fetching odds for single game: {e}")
    return game_info


def get_odds(page, sports):
    odds = {}
    for idx, sport in enumerate(sports):
        try:
            sport.click()
        except Exception as e:
            print(f"Error clicking sport: {e} at index {idx}")
            continue

        try:
            division = page.wait_for_selector(".card-bottom-left-info__name", timeout=4000).inner_text()
            print(division)
        except Exception as e:
            print(f"Error fetching division name: {e}")
            continue

        games_in_division = []
        try:
            games = page.locator(".card-shared-container")
            game_count = games.count()

            for i in range(game_count):
                games_in_division.append(get_odds_for_single_game(page, games.nth(i)))
        except Exception as e:
            print(f"Error fetching games: {e}")
            continue

        odds[division] = games_in_division
    return odds


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
            geolocation={"latitude": 43.0731, "longitude": -89.4012},  # Madison, WI
            permissions=["geolocation"]  # Allow geolocation
        )
        page = context.new_page()
        page.goto("https://sports.getfliff.com")

        sports = get_games(page)
        odds = get_odds(page, sports)
        print(odds)

        context.close()
        browser.close()
        playwright.stop()



if __name__ == "__main__":
    main()
