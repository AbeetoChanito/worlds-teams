from flask import Flask, jsonify, render_template
import os
import requests
import time
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

cache = {
    "data": None,
    "timestamp": 0
}
CACHE_DURATION = 300

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

def update_cache():
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
    sorted_teams = sorted(team_counts.items(), key=lambda x: len(x[1]), reverse=True)
    sorted_result = [{"team_number": org, "qualifications": sorted(letters)} for org, letters in sorted_teams]
    cache["data"] = sorted_result
    cache["timestamp"] = time.time()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams", methods=["GET"])
def fetch_teams():
    if time.time() - cache["timestamp"] > CACHE_DURATION:
        update_cache()
    return jsonify(cache["data"])

if __name__ == "__main__":
    update_cache()
    app.run()
