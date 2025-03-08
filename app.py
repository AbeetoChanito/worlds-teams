import os
import requests
from collections import defaultdict
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()

app = Flask(__name__)

def get_teams(world_championship_id):
    ROBOTEVENTS_API_KEY = os.getenv("ROBOTEVENTS_API_KEY")
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ROBOTEVENTS_API_KEY}"
    }

    url = f"https://www.robotevents.com/api/v2/events/{world_championship_id}/teams"
    all_teams = []
    page = 1
    PER_PAGE = 250

    while True:
        response = requests.get(f"{url}?page={page}&per_page={PER_PAGE}", headers=headers)
        if response.status_code != 200:
            raise Exception(f"HTTP error, status: {response.status_code}")
        
        response_data = response.json()
        if not response_data.get("data"):
            break
        
        for team in response_data["data"]:
            all_teams.append(team["number"])
        
        page += 1
    
    return all_teams

@app.route("/teams", methods=["GET"])
def fetch_teams():
    HS_WORLD_CHAMPIONSHIP_ID = os.getenv("HS_WORLD_CHAMPIONSHIP_ID")
    MS_WORLD_CHAMPIONSHIP_ID = os.getenv("MS_WORLD_CHAMPIONSHIP_ID")
    
    all_teams = []
    if HS_WORLD_CHAMPIONSHIP_ID:
        all_teams.extend(get_teams(HS_WORLD_CHAMPIONSHIP_ID))
    if MS_WORLD_CHAMPIONSHIP_ID:
        all_teams.extend(get_teams(MS_WORLD_CHAMPIONSHIP_ID))
    
    team_counts = defaultdict(list)
    
    for team in all_teams:
        org_number = ''.join(filter(str.isdigit, team))
        letter = ''.join(filter(str.isalpha, team))
        team_counts[org_number].append(letter)
    
    filtered_teams = {org: letters for org, letters in team_counts.items() if len(letters) > 1}
    
    sorted_teams = sorted(filtered_teams.items(), key=lambda x: len(x[1]), reverse=True)
    
    sorted_result = [{"team_number": org, "qualifications": sorted(letters)} for org, letters in sorted_teams]
    
    return jsonify(sorted_result)

if __name__ == "__main__":
    app.run(debug=True)
