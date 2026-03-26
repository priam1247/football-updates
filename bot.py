import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

FB_TOKEN         = os.getenv("FB_TOKEN")
FB_PAGE_ID       = os.getenv("FB_PAGE_ID")
FOOTBALL_KEY     = os.getenv("FOOTBALL_KEY")
APIFOOTBALL_KEY  = os.getenv("APIFOOTBALL_KEY")

FOOTBALL_BASE    = "https://api.football-data.org/v4"
APIFOOTBALL_BASE = "https://v3.football.api-sports.io"
FB_POST_URL      = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
STATE_FILE       = "match_state.json"
PAGE_NAME        = "ScoreLine Live"

# ── Leagues (football-data.org) ───────────────────────────────────
LEAGUES = {
    "PL":  "Premier League",
    "PD":  "La Liga",
    "SA":  "Serie A",
    "BL1": "Bundesliga",
    "FL1": "Ligue 1",
    "CL":  "Champions League",
    "ELC": "Championship",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "BSA": "Brasileirao",
    "WC":  "FIFA World Cup",
    "EC":  "European Championship",
}

LEAGUE_FLAGS = {
    "PL":   "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "PD":   "🇪🇸",
    "SA":   "🇮🇹",
    "BL1":  "🇩🇪",
    "FL1":  "🇫🇷",
    "CL":   "🏆",
    "ELC":  "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "DED":  "🇳🇱",
    "PPL":  "🇵🇹",
    "BSA":  "🇧🇷",
    "WC":   "🌍",
    "EC":   "🇪🇺",
    "INTL": "🌍",
}

LEAGUE_HASHTAGS = {
    "PL":   "#PremierLeague #EPL",
    "PD":   "#LaLiga #SpanishFootball",
    "SA":   "#SerieA #ItalianFootball",
    "BL1":  "#Bundesliga #GermanFootball",
    "FL1":  "#Ligue1 #FrenchFootball",
    "CL":   "#ChampionsLeague #UCL",
    "ELC":  "#Championship #EFL",
    "DED":  "#Eredivisie #DutchFootball",
    "PPL":  "#PrimeiraLiga #PortugueseFootball",
    "BSA":  "#Brasileirao #BrazilianFootball",
    "WC":   "#WorldCup #FIFA",
    "EC":   "#EURO #EuropeanChampionship",
    "INTL": "#InternationalFootball #WorldCup2026",
}

# ── Fan engagement questions ──────────────────────────────────────
GOAL_QUESTIONS = [
    "Who saw that coming? 😱",
    "What a strike! Did you see it live? 👀",
    "The crowd is going wild! 🔥",
    "Class finish! Drop a ⚽ if you saw it!",
    "Game changer! Who wins from here? 👇",
]

HALFTIME_QUESTIONS = [
    "Who has impressed you most in the first half? 👇",
    "What changes do you expect in the second half? 🤔",
    "Still anyone's game! What's your prediction? 👇",
    "Which team has been better so far? Drop your thoughts 👇",
]

FULLTIME_QUESTIONS = [
    "Who was your Man of the Match? 🏆 Drop your pick below 👇",
    "What's your reaction? 👇",
    "Did you predict this result? 🤔",
    "Fair result or did one team deserve more? 👇",
    "Rate this match out of 10 👇",
]

LINEUP_QUESTIONS = [
    "Who's winning the midfield battle today? ⚔️",
    "Any surprise selections? 👀",
    "Is your favorite player starting? 👇",
    "Which lineup looks stronger to you? 👇",
]

MATCHDAY_QUESTIONS = [
    "Which game are you watching today? 👀",
    "Who's your pick for biggest match today? 👇",
    "Big day of football ahead! Who wins today? 🏆",
]

REDCARD_QUESTIONS = [
    "How will this change the game? 🤔",
    "Harsh or deserved? Drop your verdict 👇",
    "Can the 10-man side hold on? 💪",
    "Did the ref make the right call? 👇",
]

# ── Filler content ────────────────────────────────────────────────
FILLER_POSTS = [
    "🔥 DEBATE | Messi vs Ronaldo — who is the greatest of all time? Drop your vote below 👇\n\n#Messi #Ronaldo #GOATDebate #Football #FootballTalk",
    "⚔️ DEBATE | Haaland vs Mbappe — who will be the best player in the world in 5 years? 👑\n\nDrop your pick below 👇\n\n#Haaland #Mbappe #Football #FutureStars",
    "🔥 DEBATE | Who is the best Premier League player of all time? 🏴󠁧󠁢󠁥󠁮󠁧󠁿\n\nDrop your GOAT below 👇\n\n#PremierLeague #EPL #Football #GOAT",
    "⚔️ DEBATE | Best rivalry in football history?\n\n🔵 Barcelona vs Real Madrid\n🔴 Man United vs Liverpool\n⚫ AC Milan vs Inter\n\nDrop your pick 👇\n\n#ElClasico #Football #Rivalry #FootballDebate",
    "🔥 DEBATE | Who is the best African footballer of all time? 🌍\n\nDrop your GOAT below 👇\n\n#AfricanFootball #Football #GOAT #FootballTalk",
    "🐐 LEGEND | Ronaldinho was one of the most entertaining players to ever play the game. Pure magic with the ball. 🔥\n\nDo you agree? 👇\n\n#Ronaldinho #Football #Legend #FootballHistory",
    "🐐 LEGEND | Thierry Henry scored 175 Premier League goals for Arsenal. One of the greatest strikers ever. 🏴󠁧󠁢󠁥󠁮󠁧󠁿\n\nWas he the best striker in PL history? 👇\n\n#TierryHenry #Arsenal #PremierLeague #Legend",
    "🐐 LEGEND | Zinedine Zidane won the World Cup, Euro, and Champions League. The complete midfielder. 🏆\n\nTop 5 player of all time? Drop your thoughts 👇\n\n#Zidane #France #Legend #Football",
    "🐐 LEGEND | Pele scored over 1000 career goals. A number that may never be matched. 🌍\n\nGreatest footballer ever? 👇\n\n#Pele #Brazil #Football #Legend",
    "🐐 LEGEND | Paolo Maldini played for AC Milan for 25 years. The greatest defender of all time? 🇮🇹\n\nDrop your GOAT defender below 👇\n\n#Maldini #ACMilan #SerieA #Defender #Legend",
    "📌 RECORD | Lionel Messi scored 91 goals in a single calendar year in 2012. Will this record ever be broken? 🏆\n\nDrop your thoughts 👇\n\n#Messi #Record #Football #Goals",
    "📌 RECORD | Real Madrid have won the Champions League 15 times. The most successful club in UCL history. 🏆\n\nCan anyone catch them? 👇\n\n#RealMadrid #UCL #ChampionsLeague #Record",
    "📌 RECORD | Cristiano Ronaldo is the all-time top scorer in international football with over 130 goals. 🇵🇹\n\nWill anyone ever beat this? 👇\n\n#Ronaldo #Portugal #Goals #Record #Football",
    "😱 DID YOU KNOW | The fastest goal in football history was scored after just 2.4 seconds! ⚡\n\nWould you have even noticed? 😂 Drop a reaction below 👇\n\n#Football #FunFacts #FootballTrivia",
    "😱 DID YOU KNOW | Brazil is the only country to have played in every single FIFA World Cup. 🇧🇷🌍\n\nDid you know this? Drop a 🇧🇷 below if you did!\n\n#Brazil #WorldCup #FIFA #FootballFacts",
    "😱 DID YOU KNOW | The Premier League ball travels at over 80mph when struck by top players. ⚡\n\nInsane right? 😱 Drop a reaction 👇\n\n#PremierLeague #Football #FunFacts",
    "📣 FAN POLL | Which is the best league in the world right now? 🌍\n\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League\n🇪🇸 La Liga\n🇩🇪 Bundesliga\n🇮🇹 Serie A\n\nDrop your pick below 👇\n\n#Football #BestLeague #FootballTalk #Poll",
    "📣 FAN POLL | Who is the best young player in the world right now? 🌟\n\n⭐ Yamal\n⭐ Bellingham\n⭐ Endrick\n⭐ Camavinga\n\nDrop your pick 👇\n\n#Football #YoungPlayers #NextGen #Poll",
    "📣 FAN POLL | What is the greatest goal you have ever seen? ⚽\n\nDrop the player and match below 👇\n\n#Football #GreatestGoals #FootballMoments #Poll",
    "🌍 WORLD CUP 2026 | The tournament is getting closer. Which country do you think will win? 🏆\n\nDrop your pick below 👇\n\n#WorldCup2026 #FIFA #Football #WorldCup",
    "🌍 WORLD CUP 2026 | USA, Canada and Mexico will host the biggest World Cup ever. 48 teams, 104 matches! 🔥\n\nAre you excited? 👇\n\n#WorldCup2026 #FIFA #Football",
]

# ── Persistent state ──────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return (
                    set(data.get("goals", [])),
                    set(data.get("cards", [])),
                    set(data.get("lineups", [])),
                    set(data.get("halftimes", [])),
                    set(data.get("fulltimes", [])),
                    set(data.get("matchdays", [])),
                    set(data.get("next_fixtures", [])),
                    set(data.get("filler_posted", [])),
                )
        except Exception:
            pass
    return set(), set(), set(), set(), set(), set(), set(), set()

def save_state(goals, cards, lineups, halftimes, fulltimes,
               matchdays, next_fixtures, filler_posted):
    with open(STATE_FILE, "w") as f:
        json.dump({
            "goals":         list(goals),
            "cards":         list(cards),
            "lineups":       list(lineups),
            "halftimes":     list(halftimes),
            "fulltimes":     list(fulltimes),
            "matchdays":     list(matchdays),
            "next_fixtures": list(next_fixtures),
            "filler_posted": list(filler_posted),
        }, f)

(posted_goals, posted_cards, posted_lineups, posted_halftimes,
 posted_ft, posted_matchdays, posted_next_fixtures,
 posted_filler) = load_state()

last_filler_time = 0

# ── API-Football smart request budget tracker ─────────────────────
# Free plan = 100 requests/day. We track usage to never go over.
apif_requests_today  = 0
apif_last_reset_date = None

def apif_budget_reset():
    """Reset counter at midnight UTC every day."""
    global apif_requests_today, apif_last_reset_date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if apif_last_reset_date != today:
        apif_requests_today  = 0
        apif_last_reset_date = today

def apif_can_call():
    """Return True only if we still have budget remaining."""
    apif_budget_reset()
    # Keep 10 requests as safety buffer
    return apif_requests_today < 90

# ── International match cache ─────────────────────────────────────
# Fetch today's international fixture IDs ONCE, reuse all day.
# Only re-poll live scores using /fixtures?live=all (1 call covers ALL live games)
_intl_fixture_ids   = []      # list of API-Football fixture IDs for today
_intl_fixtures_date = None    # date they were fetched for
_intl_last_live_check = 0     # timestamp of last live poll
INTL_LIVE_POLL_INTERVAL = 60  # poll live games every 60 seconds

# ── football-data.org helper ──────────────────────────────────────
def football_get(path):
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    try:
        r = requests.get(f"{FOOTBALL_BASE}{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            print("[WARN] football-data.org rate limit hit — waiting 60s")
            time.sleep(60)
    except Exception as e:
        print(f"[ERROR] football-data.org request failed: {e}")
    return None

# ── API-Football helper ───────────────────────────────────────────
def apifootball_get(path):
    """Call API-Football. Tracks daily budget. Returns None if over limit."""
    global apif_requests_today

    if not APIFOOTBALL_KEY:
        print("[INTL] ⚠️  APIFOOTBALL_KEY missing — international matches disabled!")
        return None

    if not apif_can_call():
        print(f"[INTL] ⚠️  Daily budget reached ({apif_requests_today}/90) — skipping API-Football call")
        return None

    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key":  APIFOOTBALL_KEY,
    }
    try:
        r = requests.get(f"{APIFOOTBALL_BASE}{path}", headers=headers, timeout=10)
        apif_requests_today += 1

        if r.status_code == 200:
            data   = r.json()
            errors = data.get("errors", {})
            if errors:
                print(f"[INTL] ⚠️  API-Football error in response: {errors}")
                return None
            remaining = r.headers.get("x-ratelimit-requests-remaining", "?")
            print(f"[INTL] API-Football OK — used {apif_requests_today} req today, {remaining} remaining on server")
            return data
        else:
            print(f"[INTL] ⚠️  API-Football HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[ERROR] API-Football request failed: {e}")
    return None

# ── STEP 1: Fetch today's international fixture IDs (once per day) ─
def fetch_intl_fixture_ids_today():
    """
    Called ONCE at startup and once per day at midnight.
    Fetches all of today's international/friendly fixture IDs from API-Football.
    Costs exactly 1 request per day.
    """
    global _intl_fixture_ids, _intl_fixtures_date

    today = datetime.utcnow().strftime("%Y-%m-%d")
    if _intl_fixtures_date == today and _intl_fixture_ids:
        return  # Already fetched today — do nothing

    print(f"[INTL] Fetching today's international fixture IDs for {today}...")
    data = apifootball_get(f"/fixtures?date={today}")

    if not data:
        print("[INTL] Could not fetch fixture IDs — internationals disabled today")
        _intl_fixture_ids   = []
        _intl_fixtures_date = today
        return

    # Keywords to IDENTIFY international matches
    INTL_KEYWORDS = [
        "world cup", "qualification", "qualifier", "nations league",
        "friendly", "friendlies", "international", "continental",
        "afcon", "africa cup", "gold cup", "concacaf", "copa america",
        "afc", "caf", "conmebol", "uefa", "fifa", "playoff",
        "olympics", "olympic", "pan american", "caribbean",
        "asian cup", "arab cup", "amical", "amistoso", "testspiel",
        "copa", "selecao", "seleccion",
    ]

    # Keywords to EXCLUDE domestic club competitions
    CLUB_KEYWORDS = [
        "premier league", "la liga", "serie a", "bundesliga", "ligue 1",
        "ligue 2", "championship", "eredivisie", "primeira liga",
        "super lig", "mls", "a-league", "j1 league", "j2 league",
        "k league", "liga mx", "brasileirao", "serie b", "serie c",
        "scottish", "belgian", "swiss super", "austrian", "greek super",
        "ukrainian", "russian premier", "segunda", "regionalliga",
        "fa cup", "copa del rey", "dfb-pokal", "coppa italia",
        "coupe de france", "carabao", "league cup",
        "champions league", "europa league", "conference league",
        "super cup", "supercopa", "supercoppa", "community shield",
    ]

    # Countries that signal international competition
    INTL_COUNTRIES = {
        "world", "europe", "south america", "north america",
        "africa", "asia", "oceania", "concacaf",
    }

    ids = []
    total = len(data.get("response", []))

    for fixture in data.get("response", []):
        league      = fixture.get("league", {})
        league_name = league.get("name", "").lower().strip()
        league_type = league.get("type", "").lower().strip()
        country     = league.get("country", "").lower().strip()

        # Hard skip club competitions
        if any(kw in league_name for kw in CLUB_KEYWORDS):
            continue

        # Accept if any signal matches
        is_intl = (
            league_type in ("cup", "international", "friendly") or
            any(kw in league_name for kw in INTL_KEYWORDS) or
            country in INTL_COUNTRIES
        )

        if is_intl:
            fix_id = fixture.get("fixture", {}).get("id")
            if fix_id:
                ids.append(fix_id)

    _intl_fixture_ids   = ids
    _intl_fixtures_date = today
    print(f"[INTL] Found {len(ids)} international fixtures today (from {total} total)")

# ── STEP 2: Poll live scores for international matches ─────────────
def get_live_intl_matches():
    """
    Uses /fixtures?live=all — ONE call covers ALL live matches at once.
    Only returns matches that are in today's international fixture ID list.
    Respects the 60-second polling interval.
    """
    global _intl_last_live_check

    if not _intl_fixture_ids:
        return []

    now = time.time()
    if now - _intl_last_live_check < INTL_LIVE_POLL_INTERVAL:
        return []  # Too soon to poll again

    _intl_last_live_check = now

    data = apifootball_get("/fixtures?live=all")
    if not data:
        return []

    live_fixtures = data.get("response", [])
    live_intl     = [f for f in live_fixtures
                     if f.get("fixture", {}).get("id") in _intl_fixture_ids]

    print(f"[INTL] Live poll: {len(live_fixtures)} total live, {len(live_intl)} are today's internationals")
    return live_intl

# ── STEP 3: Get ALL today's intl matches (for preview + status) ────
def get_all_intl_matches_today():
    """
    Returns normalized match dicts for ALL of today's international matches.
    For scheduled/finished matches, fetches their current status in bulk.
    Called once per check cycle to build the full picture.
    """
    if not _intl_fixture_ids:
        return []

    # Fetch status for all today's intl fixtures in one call using IDs
    ids_str = "-".join(str(i) for i in _intl_fixture_ids[:20])  # max 20 per call
    data    = apifootball_get(f"/fixtures?ids={ids_str}")

    if not data:
        return []

    return [normalize_apif_fixture(f) for f in data.get("response", [])]

# ── STEP 4: Normalize API-Football fixture to our format ───────────
def normalize_apif_fixture(fixture):
    """Convert API-Football fixture dict to our standard match format."""
    fix    = fixture.get("fixture", {})
    teams  = fixture.get("teams", {})
    goals  = fixture.get("goals", {})
    score  = fixture.get("score", {})
    league = fixture.get("league", {})
    status = fix.get("status", {}).get("short", "")

    STATUS_MAP = {
        "NS":   "SCHEDULED",
        "TBD":  "TIMED",
        "1H":   "IN_PLAY",
        "2H":   "IN_PLAY",
        "ET":   "IN_PLAY",
        "P":    "IN_PLAY",
        "BT":   "PAUSED",
        "HT":   "PAUSED",
        "FT":   "FINISHED",
        "AET":  "FINISHED",
        "PEN":  "FINISHED",
        "AWD":  "FINISHED",
        "WO":   "FINISHED",
        "PST":  "POSTPONED",
        "CANC": "CANCELLED",
        "ABD":  "CANCELLED",
    }

    norm_status = STATUS_MAP.get(status, "SCHEDULED")
    comp_name   = league.get("name", "International")
    home_name   = teams.get("home", {}).get("name", "")
    away_name   = teams.get("away", {}).get("name", "")

    FLAG_MAP = {
        "world cup":      "🌍",
        "nations league": "🏆",
        "euro":           "🇪🇺",
        "uefa":           "🇪🇺",
        "afcon":          "🌍",
        "africa cup":     "🌍",
        "concacaf":       "🌎",
        "gold cup":       "🌎",
        "copa america":   "🌎",
        "afc":            "🌏",
        "asian":          "🌏",
        "olympics":       "🏅",
        "friendly":       "🤝",
        "amical":         "🤝",
        "amistoso":       "🤝",
        "qualification":  "🌍",
        "qualifier":      "🌍",
        "playoff":        "🌍",
    }
    comp_lower = comp_name.lower()
    comp_flag  = next((v for k, v in FLAG_MAP.items() if k in comp_lower), "🌍")

    # Extract goals and bookings from events if present
    match_goals    = []
    match_bookings = []
    for event in fixture.get("events", []):
        etype  = event.get("type", "").lower()
        detail = event.get("detail", "").lower()
        minute = event.get("time", {}).get("elapsed", "?")
        player = event.get("player", {}).get("name", "Unknown")
        assist = event.get("assist", {}) or {}
        team   = event.get("team", {}).get("name", "")

        if etype == "goal" and "own" not in detail and "missed" not in detail and "penalty" not in detail:
            match_goals.append({
                "minute": minute,
                "scorer": {"name": player},
                "assist": {"name": assist.get("name", "")} if assist.get("name") else {},
                "team":   {"shortName": team},
            })
        elif etype == "goal" and "penalty" in detail:
            match_goals.append({
                "minute": minute,
                "scorer": {"name": f"{player} (pen)"},
                "assist": {},
                "team":   {"shortName": team},
            })
        elif etype == "card" and "red" in detail:
            match_bookings.append({
                "minute": minute,
                "card":   "RED_CARD",
                "player": {"name": player},
                "team":   {"shortName": team},
            })

    return {
        "id":       f"apif_{fix.get('id', '')}",
        "utcDate":  fix.get("date", ""),
        "status":   norm_status,
        "competition": {
            "code": "INTL",
            "name": comp_name,
            "flag": comp_flag,
        },
        "homeTeam": {
            "id":        str(teams.get("home", {}).get("id", "")),
            "name":      home_name,
            "shortName": home_name,
        },
        "awayTeam": {
            "id":        str(teams.get("away", {}).get("id", "")),
            "name":      away_name,
            "shortName": away_name,
        },
        "score": {
            "halfTime": {
                "home": score.get("halftime", {}).get("home"),
                "away": score.get("halftime", {}).get("away"),
            },
            "fullTime": {
                "home": goals.get("home"),
                "away": goals.get("away"),
            },
        },
        "goals":    match_goals,
        "bookings": match_bookings,
        "lineups":  fixture.get("lineups", []),
        "_apif_fixture_id": fix.get("id", ""),
        "_comp_name":       comp_name,
        "_comp_flag":       comp_flag,
    }

# ── Post to Facebook ──────────────────────────────────────────────
def post_to_facebook(message):
    payload = {"message": message, "access_token": FB_TOKEN}
    try:
        r = requests.post(FB_POST_URL, data=payload, timeout=10)
        if r.status_code == 200:
            print(f"[POSTED] {message[:70]}...")
            return True
        else:
            print(f"[ERROR] FB post failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"[ERROR] FB post exception: {e}")
    return False

# ── Score helpers ─────────────────────────────────────────────────
def get_score(match):
    home = match["homeTeam"]["shortName"]
    away = match["awayTeam"]["shortName"]
    ft   = match["score"]["fullTime"]
    ht   = match["score"]["halfTime"]
    hs   = ft["home"] if ft["home"] is not None else (ht["home"] or 0)
    as_  = ft["away"] if ft["away"] is not None else (ht["away"] or 0)
    return home, away, hs, as_

def get_league_code(league_name):
    return next((c for c, n in LEAGUES.items() if n == league_name), "INTL")

def get_flag(league_name):
    code = get_league_code(league_name)
    return LEAGUE_FLAGS.get(code, "🌍")

def get_hashtags(league_name):
    code = get_league_code(league_name)
    return LEAGUE_HASHTAGS.get(code, "#Football #InternationalFootball #WorldCup2026")

def is_heavy_matchday(all_matches_today):
    big_leagues = {"PL", "PD", "SA", "BL1", "FL1", "CL", "WC", "EC"}
    total       = sum(len(m) for m in all_matches_today.values())
    has_big     = any(c in big_leagues for c in all_matches_today)
    return total >= 5 or has_big

# ── Matchday preview ──────────────────────────────────────────────
def handle_matchday_preview(all_matches_today):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    key   = f"matchday_{today}"
    if key in posted_matchdays or not all_matches_today:
        return

    heavy = is_heavy_matchday(all_matches_today)
    lines = ["📅 MATCHES OF THE DAY\n"]

    for league_code, matches in all_matches_today.items():
        flag        = LEAGUE_FLAGS.get(league_code, "🌍")
        league_name = LEAGUES.get(league_code, "International / Friendlies")

        if heavy and league_code not in {
            "PL","PD","SA","BL1","FL1","CL","WC","EC","INTL"
        }:
            continue

        lines.append(f"{flag} {league_name}")
        for m in matches:
            home = m["homeTeam"]["shortName"]
            away = m["awayTeam"]["shortName"]
            try:
                kickoff  = datetime.strptime(m.get("utcDate",""), "%Y-%m-%dT%H:%M:%SZ")
                time_str = kickoff.strftime("%H:%M UTC")
            except Exception:
                time_str = "TBD"
            lines.append(f"  ⚔️  {home} vs {away} — {time_str}")
        lines.append("")

    if len(lines) <= 1:
        return

    question = random.choice(MATCHDAY_QUESTIONS)
    lines.append(question)
    lines.append("")
    lines.append("#MatchDay #FootballLive #Football #ScoreLineLive")
    lines.append(f"\nFollow {PAGE_NAME} for live updates 🔔")

    posted_matchdays.add(key)
    save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
               posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
    post_to_facebook("\n".join(lines))

# ── Lineups ───────────────────────────────────────────────────────
def handle_lineups(match, league_name):
    match_id = match["id"]
    key      = f"{match_id}_lineup"
    if key in posted_lineups:
        return

    home    = match["homeTeam"]["shortName"]
    away    = match["awayTeam"]["shortName"]
    lineups = match.get("lineups", [])
    if len(lineups) < 2:
        return

    def format_players(lineup):
        players = lineup.get("startXI", [])
        if not players:
            return "  Lineup not available"
        return "\n".join(
            f"  {i+1}. {p.get('player',{}).get('name','')}"
            for i, p in enumerate(players)
        )

    flag     = get_flag(league_name)
    hashtags = get_hashtags(league_name)
    question = random.choice(LINEUP_QUESTIONS)

    posted_lineups.add(key)
    save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
               posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
    msg = (
        f"📋 LINEUPS | {home} vs {away}\n\n"
        f"🔵 {home}:\n{format_players(lineups[0])}\n\n"
        f"🔴 {away}:\n{format_players(lineups[1])}\n\n"
        f"{question}\n\n"
        f"{flag} {league_name} | {hashtags} #Lineup #MatchDay\n\n"
        f"Follow {PAGE_NAME} for live updates 🔔"
    )
    post_to_facebook(msg)

# ── Goals ─────────────────────────────────────────────────────────
def handle_goals(match, league_name):
    match_id            = match["id"]
    home, away, hs, as_ = get_score(match)
    flag                = get_flag(league_name)
    hashtags            = get_hashtags(league_name)

    for goal in match.get("goals", []):
        scorer = goal.get("scorer", {}).get("name", "Unknown")
        assist = goal.get("assist", {})
        minute = goal.get("minute", "?")
        team   = goal.get("team", {}).get("shortName", "")
        key    = f"{match_id}_{team}_{minute}_{scorer}"

        if key not in posted_goals:
            posted_goals.add(key)
            save_state(posted_goals, posted_cards, posted_lineups,
                       posted_halftimes, posted_ft, posted_matchdays,
                       posted_next_fixtures, posted_filler)

            assist_line = ""
            if assist and assist.get("name"):
                assist_line = f"🅰️ Assist: {assist['name']}\n\n"

            question = random.choice(GOAL_QUESTIONS)
            msg = (
                f"⚽ GOAL! {scorer} scores at {minute}'\n\n"
                f"🚩 {home} {hs} — {as_} {away}\n\n"
                f"{assist_line}"
                f"{question}\n\n"
                f"{flag} {league_name} | {hashtags} #GoalAlert #LiveFootball\n\n"
                f"Follow {PAGE_NAME} for live updates 🔔"
            )
            post_to_facebook(msg)

# ── Red cards ─────────────────────────────────────────────────────
def handle_red_cards(match, league_name):
    match_id            = match["id"]
    home, away, hs, as_ = get_score(match)
    flag                = get_flag(league_name)
    hashtags            = get_hashtags(league_name)

    for booking in match.get("bookings", []):
        if booking.get("card") == "RED_CARD":
            player = booking.get("player", {}).get("name", "Unknown")
            minute = booking.get("minute", "?")
            team   = booking.get("team", {}).get("shortName", "")
            key    = f"{match_id}_{player}_{minute}"

            if key not in posted_cards:
                posted_cards.add(key)
                save_state(posted_goals, posted_cards, posted_lineups,
                           posted_halftimes, posted_ft, posted_matchdays,
                           posted_next_fixtures, posted_filler)
                question = random.choice(REDCARD_QUESTIONS)
                msg = (
                    f"🟥 RED CARD! {player} sent off at {minute}'\n\n"
                    f"🚩 {home} {hs} — {as_} {away} | {team} down to 10 men\n\n"
                    f"{question}\n\n"
                    f"{flag} {league_name} | {hashtags} #RedCard #FootballDebate\n\n"
                    f"Follow {PAGE_NAME} for live updates 🔔"
                )
                post_to_facebook(msg)

# ── Half time ─────────────────────────────────────────────────────
def handle_halftime(match, league_name):
    match_id = match["id"]
    key      = f"{match_id}_halftime"
    if key in posted_halftimes:
        return

    home     = match["homeTeam"]["shortName"]
    away     = match["awayTeam"]["shortName"]
    hs       = match["score"]["halfTime"]["home"] or 0
    as_      = match["score"]["halfTime"]["away"] or 0
    flag     = get_flag(league_name)
    hashtags = get_hashtags(league_name)

    goal_lines = []
    for g in match.get("goals", []):
        scorer = g.get("scorer", {}).get("name", "Unknown")
        minute = g.get("minute", "?")
        team   = g.get("team", {}).get("shortName", "")
        goal_lines.append(f"  ⚽ {scorer} ({minute}') — {team}")

    goals_summary = "\n".join(goal_lines) if goal_lines else "  No goals yet"
    question      = random.choice(HALFTIME_QUESTIONS)

    posted_halftimes.add(key)
    save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
               posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
    msg = (
        f"⏸️ HALF TIME | {home} {hs} — {as_} {away}\n\n"
        f"⚽ Goals so far:\n{goals_summary}\n\n"
        f"{question}\n\n"
        f"{flag} {league_name} | {hashtags} #HalfTime #FootballLive\n\n"
        f"Follow {PAGE_NAME} for live updates 🔔"
    )
    post_to_facebook(msg)

# ── Full time ─────────────────────────────────────────────────────
def handle_fulltime(match, league_name):
    match_id = match["id"]
    key      = f"{match_id}_fulltime"
    if key in posted_ft:
        return

    home, away, hs, as_ = get_score(match)
    flag     = get_flag(league_name)
    hashtags = get_hashtags(league_name)

    goal_lines = []
    for g in match.get("goals", []):
        scorer     = g.get("scorer", {}).get("name", "Unknown")
        assist     = g.get("assist", {})
        minute     = g.get("minute", "?")
        team       = g.get("team", {}).get("shortName", "")
        assist_str = f" (assist: {assist['name']})" if assist and assist.get("name") else ""
        goal_lines.append(f"  ⚽ {scorer}{assist_str} ({minute}') — {team}")

    goals_summary = "\n".join(goal_lines) if goal_lines else "  No goals"

    if hs > as_:
        result    = f"🏆 {home} win!"
        result_ht = "#" + home.replace(" ", "")
    elif as_ > hs:
        result    = f"🏆 {away} win!"
        result_ht = "#" + away.replace(" ", "")
    else:
        result    = "🤝 It's a draw!"
        result_ht = "#Draw"

    question = random.choice(FULLTIME_QUESTIONS)

    posted_ft.add(key)
    save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
               posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
    msg = (
        f"🏁 FULL TIME | {home} {hs} — {as_} {away}\n\n"
        f"{result}\n\n"
        f"⚽ Goals:\n{goals_summary}\n\n"
        f"{question}\n\n"
        f"{flag} {league_name} | {hashtags} #FullTime #MatchResult {result_ht}\n\n"
        f"Follow {PAGE_NAME} for more football updates 🔔"
    )
    post_to_facebook(msg)
    handle_next_fixture(match, league_name)

# ── Next fixture ──────────────────────────────────────────────────
def handle_next_fixture(match, league_name):
    match_id = match["id"]
    key      = f"{match_id}_nextfixture"
    if key in posted_next_fixtures:
        return

    # Only fetch next fixture for club league matches (not internationals)
    code = get_league_code(league_name)
    if code in ("INTL", ""):
        return

    home    = match["homeTeam"]["shortName"]
    away    = match["awayTeam"]["shortName"]
    home_id = match["homeTeam"].get("id", "")
    away_id = match["awayTeam"].get("id", "")
    flag    = get_flag(league_name)
    hashtags = get_hashtags(league_name)

    home_next = None
    away_next = None

    try:
        today  = datetime.utcnow().strftime("%Y-%m-%d")
        future = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
        data   = football_get(
            f"/competitions/{code}/matches"
            f"?dateFrom={today}&dateTo={future}&status=SCHEDULED"
        )
        if data:
            for m in data.get("matches", []):
                mhome = m["homeTeam"].get("id")
                maway = m["awayTeam"].get("id")
                if not home_next and (mhome == home_id or maway == home_id):
                    home_next = m
                if not away_next and (mhome == away_id or maway == away_id):
                    away_next = m
                if home_next and away_next:
                    break
    except Exception as e:
        print(f"[ERROR] Next fixture fetch failed: {e}")

    lines = [f"🔜 NEXT FIXTURES\n"]
    if home_next:
        nh = home_next["homeTeam"]["shortName"]
        na = home_next["awayTeam"]["shortName"]
        try:
            nd = datetime.strptime(
                home_next.get("utcDate",""), "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %b %Y")
        except Exception:
            nd = "TBD"
        lines.append(f"  ⚔️  {nh} vs {na} — {nd}")

    if away_next and away_next != home_next:
        nh = away_next["homeTeam"]["shortName"]
        na = away_next["awayTeam"]["shortName"]
        try:
            nd = datetime.strptime(
                away_next.get("utcDate",""), "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %b %Y")
        except Exception:
            nd = "TBD"
        lines.append(f"  ⚔️  {nh} vs {na} — {nd}")

    if len(lines) <= 1:
        return

    lines.append("\nPredictions already? 👀")
    lines.append(f"\n{flag} {league_name} | {hashtags} #NextFixture #Football")
    lines.append(f"\nFollow {PAGE_NAME} for live updates 🔔")

    posted_next_fixtures.add(key)
    save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
               posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
    post_to_facebook("\n".join(lines))

# ── Filler ────────────────────────────────────────────────────────
def handle_filler(has_live_matches):
    global last_filler_time
    if has_live_matches:
        return

    now = time.time()
    if now - last_filler_time < 1800:
        return

    available = [p for p in FILLER_POSTS if p[:50] not in posted_filler]
    if not available:
        posted_filler.clear()
        available = FILLER_POSTS

    post = random.choice(available)
    if post_to_facebook(post):
        posted_filler.add(post[:50])
        last_filler_time = now
        save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
                   posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
        print(f"[FILLER] Posted filler content.")

# ── Process a single match ────────────────────────────────────────
def process_match(match, league_name):
    """Run all event handlers for one match."""
    status = match.get("status")

    # Lineups — 45 to 75 mins before kickoff
    if status in ("TIMED", "SCHEDULED"):
        kickoff_str = match.get("utcDate", "")
        if kickoff_str:
            try:
                kickoff = datetime.strptime(kickoff_str, "%Y-%m-%dT%H:%M:%SZ")
                now     = datetime.utcnow()
                if timedelta(minutes=45) <= kickoff - now <= timedelta(minutes=75):
                    handle_lineups(match, league_name)
            except Exception:
                pass

    if status == "IN_PLAY":
        handle_goals(match, league_name)
        handle_red_cards(match, league_name)

    if status == "PAUSED":
        handle_halftime(match, league_name)

    if status == "FINISHED":
        handle_fulltime(match, league_name)

# ── Main check cycle ──────────────────────────────────────────────
matchday_posted_today = None

def check_matches():
    global matchday_posted_today
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # ── Step 1: Ensure we have today's intl fixture IDs (costs 1 req, once/day)
    fetch_intl_fixture_ids_today()

    all_matches_today = {}

    # ── Step 2: Fetch club league matches via football-data.org (free, unlimited)
    for code in LEAGUES:
        if code in ("WC", "EC", "INTL"):
            continue
        data = football_get(
            f"/competitions/{code}/matches?dateFrom={today}&dateTo={today}"
        )
        if data:
            matches = data.get("matches", [])
            if matches:
                all_matches_today[code] = matches

    # Also check WC and EC via football-data.org (they cover these free)
    for code in ("WC", "EC"):
        data = football_get(
            f"/competitions/{code}/matches?dateFrom={today}&dateTo={today}"
        )
        if data:
            matches = data.get("matches", [])
            if matches:
                all_matches_today[code] = matches

    # ── Step 3: Get international matches
    # Use live endpoint if any intl games should be live now
    # otherwise use the full fixture list for status checks
    intl_matches = []

    if _intl_fixture_ids:
        # Try live poll first (very cheap — 1 call covers all)
        live_fixtures = get_live_intl_matches()
        if live_fixtures:
            intl_matches = [normalize_apif_fixture(f) for f in live_fixtures]
        else:
            # No live games right now — fetch full status for today's fixtures
            intl_matches = get_all_intl_matches_today()

    if intl_matches:
        all_matches_today["INTL"] = intl_matches
        LEAGUES["INTL"]           = "International / Friendlies"

    # ── Step 4: Check if anything is live
    has_live = any(
        m.get("status") in ("IN_PLAY", "PAUSED")
        for matches in all_matches_today.values()
        for m in matches
    )

    # ── Step 5: Post matchday preview once per day
    if matchday_posted_today != today:
        handle_matchday_preview(all_matches_today)
        matchday_posted_today = today

    # ── Step 6: Process every match
    for code, matches in all_matches_today.items():
        for match in matches:
            if code == "INTL":
                league_name = match.get("_comp_name", "International / Friendlies")
            else:
                league_name = LEAGUES.get(code, "Football")
            process_match(match, league_name)

    # ── Step 7: Post filler if nothing is live
    if not has_live:
        handle_filler(has_live)

    # ── Step 8: Log API-Football budget
    if APIFOOTBALL_KEY:
        print(f"[BUDGET] API-Football used today: {apif_requests_today}/90 requests")

# ── Run ───────────────────────────────────────────────────────────
def run():
    print(f"{PAGE_NAME} Match Bot started...")
    print(f"Monitoring: {', '.join(list(LEAGUES.values())[:6])} + internationals")
    print("Posting: Matchday preview, Lineups, Goals + Assists,")
    print("         Red Cards, Half Time, Full Time, Next Fixture, Filler")
    print(f"API-Football budget: 90 calls/day max (free plan safe)\n")

    while True:
        try:
            check_matches()
        except Exception as e:
            print(f"[ERROR] {e}")
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Checked. Waiting 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    run()
