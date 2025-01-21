import requests
from datetime import datetime

#TODO: work on fixing the live maybe? not sure how it works with live games

#maybe change name, but this func will add all of the IDS
def get_odds_per_league(odds_info):
    try:
        odds = {}

        def initialize_market(market_id):
            #create the market id for each game and init the away and home dict
            if market_id not in odds:
                odds[market_id] = {"away": {}, "home": {}}

        def process_spread(odd, market_id):
            # if dict matches Away set team to away else home
            team = "away" if odd["outcomeType"] == "Away" else "home"
            #set away or home spread value and odds
            odds[market_id][team]["spread"] = {"value": odd["points"], "odds": odd["displayOdds"]["american"]}
            #if we havent seen this team yet, add the team name
            if "team" not in odds[market_id][team]:
                odds[market_id][team]["team"] = odd["label"]

        def process_over_under(odd, market_id):
            #if label is over set var to over else under
            over_under_key = "over" if odd["label"] == "Over" else "under"
            #set the over under value and odds
            odds[market_id][over_under_key] = {"value": odd["points"], "odds": odd["displayOdds"]["american"]}

        def process_moneyline(odd, market_id):
            # if dict matches Away set team to away else home
            team = "away" if odd["outcomeType"] == "Away" else "home"
            # set moneyline for away or home team
            odds[market_id][team]["moneyline"] = odd["displayOdds"]["american"]
            #if we havent seen this team yet, add the team name
            if "team" not in odds[market_id][team]:
                odds[market_id][team]["team"] = odd["label"]

        # Loop through odds
        for odd in odds_info:
            #seperate out marketID(value after _)
            market_id = odd["marketId"].split("_")[1]
            initialize_market(market_id)
            #spread
            if "HC" in odd["id"]:
                process_spread(odd, market_id)
            #total
            elif "OU" in odd["id"]:
                process_over_under(odd, market_id)
            #moneyline
            else:
                process_moneyline(odd, market_id)
        
        #replace market id with a team name
        odds =  {odd["away"]["team"] if odd["away"] else odd["home"]["team"]: odd for key, odd in odds.items()}
        # print(odds)
    except Exception as e:
        print("error getting the odds in the league", e)
    return odds



def sort_data_per_league(league_data):
    
    games = []
    # try to run parallel, so this loop and other loop at same time
    try:
        for team in league_data["events"]:
            date = team["startEventDate"]
            parsed_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f0Z')
            formatted_date = parsed_date.strftime('%b %#d, %Y')

            single_game_info = {"date" : formatted_date}
            single_game_info["home"] = team["participants"][0]["name"]
            single_game_info["away"] = team["participants"][1]["name"]
            games.append(single_game_info)
    except Exception as e:
        print("error setting up game dicts", e)
    #call func to filter bet info
    odds = get_odds_per_league(league_data["selections"])
    #loop through all events
    try:
        for game in games:
            #see if matching key is the home or away team in this game and set it to a var
            team = game["home"] if game["home"] in odds else game["away"]
            # need to do odds[team] because thats the maching key
            game["home"] = odds[team]["home"]
            game["away"] = odds[team]["away"]
            #if we found an over set it, else set to None
            game["over"] = odds[team]["over"] if "over" in odds[team] else None
            #if we found an under set it, else set to None
            game["under"] = odds[team]["under"] if "under" in odds[team] else None
    except Exception as e:
        print("error adding odds to game dicts", e, "league odds", odds)


    
    return games


def request_per_league(URLS, HEADERS):
    odds = {}
    for league, url in URLS.items():
        try:
            r = requests.get(url = url, headers=HEADERS)
            data= r.json()
            odds[league] = sort_data_per_league(data)
        except Exception as e:
            print("error making requests", e)
    return odds

def main():
    URLS = {}
    URLS["NFL"] = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/88808"
    URLS["NHL"] = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42133"
    URLS["NBA"] = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648"
    URLS["NCAAB"] = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/92483"
    URLS["NCAAF"] = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/87637"
    HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://sportsbook.draftkings.com",
        "referer": "https://sportsbook.draftkings.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    odds = request_per_league(URLS, HEADERS)
    print(odds)


if __name__ == "__main__":
    main()