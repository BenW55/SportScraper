import requests
from datetime import datetime

#maybe change name, but this func will add all of the IDS
def get_odds_per_league(odds_info):
    odds = {}

    def initialize_market(market_id):
        
        if market_id not in odds:
            odds[market_id] = {"away": {}, "home": {}}

    def process_spread(odd, market_id):
        
        team = "away" if odd["outcomeType"] == "Away" else "home"
        odds[market_id][team]["spread"] = {"value": odd["points"], "odds": odd["displayOdds"]["american"]}
        if "team" not in odds[market_id][team]:
            odds[market_id][team]["team"] = odd["label"]

    def process_over_under(odd, market_id):
        
        over_under_key = "over" if odd["label"] == "Over" else "under"
        odds[market_id][over_under_key] = {"value": odd["points"], "odds": odd["displayOdds"]["american"]}

    def process_moneyline(odd, market_id):
        
        team = "away" if odd["outcomeType"] == "Away" else "home"
        odds[market_id][team]["moneyline"] = odd["displayOdds"]["american"]
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
    return odds



def sort_data_per_league(league_data):
    games = []
    # try to run parallel, so this loop and other loop at same time
    for team in league_data["events"]:
        date = team["startEventDate"]
        parsed_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f0Z')
        formatted_date = parsed_date.strftime('%b %#d, %Y')

        single_game_info = {"date" : formatted_date}
        single_game_info["home"] = team["participants"][0]["name"]
        single_game_info["away"] = team["participants"][1]["name"]
        games.append(single_game_info)
    odds = get_odds_per_league(league_data["selections"])
    #TODO: get market id somehow
    #call func to filter bet info

    #loop through all events
    for game in games:
    #check for key matches for home and away team, and add to that game
        team = game["home"] if game["home"] in odds else game["away"]
        game["home"] = odds[team]["home"]
        game["away"] = odds[team]["away"]
        game["over"] = odds[team]["over"]
        game["under"] = odds[team]["under"]



    
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