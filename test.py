import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FB_TOKEN        = os.getenv("FB_TOKEN")
FB_PAGE_ID      = os.getenv("FB_PAGE_ID")
FOOTBALL_KEY    = os.getenv("FOOTBALL_KEY")
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY")

def test_credentials():
    print("Checking Railway variables...\n")
    ok = True

    checks = [
        ("FB_TOKEN",        FB_TOKEN),
        ("FB_PAGE_ID",      FB_PAGE_ID),
        ("FOOTBALL_KEY",    FOOTBALL_KEY),
        ("APIFOOTBALL_KEY", APIFOOTBALL_KEY),
    ]

    for name, val in checks:
        if not val or "your_" in str(val):
            print(f"❌ {name} is NOT set")
            ok = False
        else:
            print(f"✅ {name} loaded")

    return ok

def test_facebook():
    print("\nTesting Facebook connection...")
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
    msg = (
        "🧪 Bot Test Post\n\n"
        "🚩 Live: Brazil 1 — 0 France\n\n"
        "⚽ Goal: Vinicius Jr (23')\n\n"
        "🌍 International Friendly | ScoreLine Live\n\n"
        "(Test post — delete after checking)"
    )
    r = requests.post(url, data={"message": msg, "access_token": FB_TOKEN}, timeout=10)
    if r.status_code == 200:
        print("✅ Facebook OK — test post is live on your page!")
    else:
        print(f"❌ Facebook FAILED: {r.status_code}")
        print(r.text[:300])

def test_football_data():
    print("\nTesting football-data.org...")
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    r = requests.get("https://api.football-data.org/v4/competitions/PL",
                     headers=headers, timeout=10)
    if r.status_code == 200:
        print("✅ football-data.org OK!")
    else:
        print(f"❌ football-data.org FAILED: {r.status_code}")
        print(r.text[:300])

def test_apifootball():
    print("\nTesting API-Football (internationals)...")
    if not APIFOOTBALL_KEY:
        print("❌ APIFOOTBALL_KEY not set — internationals will be disabled")
        return

    today   = datetime.utcnow().strftime("%Y-%m-%d")
    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key":  APIFOOTBALL_KEY,
    }
    r = requests.get(
        f"https://v3.football.api-sports.io/fixtures?date={today}",
        headers=headers, timeout=10
    )
    if r.status_code == 200:
        data     = r.json()
        errors   = data.get("errors", {})
        if errors:
            print(f"❌ API-Football returned error: {errors}")
            return
        total     = len(data.get("response", []))
        remaining = r.headers.get("x-ratelimit-requests-remaining", "?")
        print(f"✅ API-Football OK! Found {total} fixtures today.")
        print(f"   Requests remaining today: {remaining}/100")
    else:
        print(f"❌ API-Football FAILED: {r.status_code}")
        print(r.text[:300])

def test_live_endpoint():
    print("\nTesting API-Football live endpoint...")
    if not APIFOOTBALL_KEY:
        print("⏭️  Skipped (no APIFOOTBALL_KEY)")
        return

    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key":  APIFOOTBALL_KEY,
    }
    r = requests.get(
        "https://v3.football.api-sports.io/fixtures?live=all",
        headers=headers, timeout=10
    )
    if r.status_code == 200:
        data  = r.json()
        total = len(data.get("response", []))
        print(f"✅ Live endpoint OK! {total} matches currently live.")
    else:
        print(f"❌ Live endpoint FAILED: {r.status_code}")

if __name__ == "__main__":
    print("=" * 42)
    print("  ScoreLine Live — Bot Test Mode")
    print("=" * 42 + "\n")

    if test_credentials():
        test_football_data()
        test_apifootball()
        test_live_endpoint()
        test_facebook()
        print("\n✅ All tests done!")
        print("If everything passed — push to GitHub and Railway will auto-deploy.")
    else:
        print("\n❌ Fix your Railway variables first then run this again.")
