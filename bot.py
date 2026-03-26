import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from reel_generator import create_and_post_reel

load_dotenv()

FB_TOKEN     = os.getenv("FB_TOKEN")
FB_PAGE_ID   = os.getenv("FB_PAGE_ID")
FOOTBALL_KEY = os.getenv("FOOTBALL_KEY")

FOOTBALL_BASE = "https://api.football-data.org/v4"
FB_POST_URL   = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
STATE_FILE    = "match_state.json"
PAGE_NAME     = "ScoreLine Live"

# ── All leagues ───────────────────────────────────────────────────
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
    "PL":  "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "PD":  "🇪🇸",
    "SA":  "🇮🇹",
    "BL1": "🇩🇪",
    "FL1": "🇫🇷",
    "CL":  "🏆",
    "ELC": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "DED": "🇳🇱",
    "PPL": "🇵🇹",
    "BSA": "🇧🇷",
    "WC":  "🌍",
    "EC":  "🇪🇺",
    "INTL": "🌍",
}

LEAGUE_HASHTAGS = {
    "PL":  "#PremierLeague #EPL",
    "PD":  "#LaLiga #SpanishFootball",
    "SA":  "#SerieA #ItalianFootball",
    "BL1": "#Bundesliga #GermanFootball",
    "FL1": "#Ligue1 #FrenchFootball",
    "CL":  "#ChampionsLeague #UCL",
    "ELC": "#Championship #EFL",
    "DED": "#Eredivisie #DutchFootball",
    "PPL": "#PrimeiraLiga #PortugueseFootball",
    "BSA": "#Brasileirao #BrazilianFootball",
    "WC":  "#WorldCup #FIFA",
    "EC":  "#EURO #EuropeanChampionship",
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

# ── Filler content library for light matchdays ────────────────────
FILLER_POSTS = [
    # Debates
    "🔥 DEBATE | Messi vs Ronaldo — who is the greatest of all time? Drop your vote below 👇\n\n#Messi #Ronaldo #GOATDebate #Football #FootballTalk",
    "⚔️ DEBATE | Haaland vs Mbappe — who will be the best player in the world in 5 years? 👑\n\nDrop your pick below 👇\n\n#Haaland #Mbappe #Football #FutureStars",
    "🔥 DEBATE | Who is the best Premier League player of all time? 🏴󠁧󠁢󠁥󠁮󠁧󠁿\n\nDrop your GOAT below 👇\n\n#PremierLeague #EPL #Football #GOAT",
    "⚔️ DEBATE | Best rivalry in football history?\n\n🔵 Barcelona vs Real Madrid\n🔴 Man United vs Liverpool\n⚫ AC Milan vs Inter\n\nDrop your pick 👇\n\n#ElClasico #Football #Rivalry #FootballDebate",
    "🔥 DEBATE | Who is the best African footballer of all time? 🌍\n\nDrop your GOAT below 👇\n\n#AfricanFootball #Football #GOAT #FootballTalk",

    # Legends
    "🐐 LEGEND | Ronaldinho was one of the most entertaining players to ever play the game. Pure magic with the ball. 🔥\n\nDo you agree? 👇\n\n#Ronaldinho #Football #Legend #FootballHistory",
    "🐐 LEGEND | Thierry Henry scored 175 Premier League goals for Arsenal. One of the greatest strikers ever. 🏴󠁧󠁢󠁥󠁮󠁧󠁿\n\nWas he the best striker in PL history? 👇\n\n#TierryHenry #Arsenal #PremierLeague #Legend",
    "🐐 LEGEND | Zinedine Zidane won the World Cup, Euro, and Champions League. The complete midfielder. 🏆\n\nTop 5 player of all time? Drop your thoughts 👇\n\n#Zidane #France #Legend #Football",
    "🐐 LEGEND | Pele scored over 1000 career goals. A number that may never be matched. 🌍\n\nGreatest footballer ever? 👇\n\n#Pele #Brazil #Football #Legend",
    "🐐 LEGEND | Paolo Maldini played for AC Milan for 25 years. The greatest defender of all time? 🇮🇹\n\nDrop your GOAT defender below 👇\n\n#Maldini #ACMilan #SerieA #Defender #Legend",

    # Records
    "📌 RECORD | Lionel Messi scored 91 goals in a single calendar year in 2012. Will this record ever be broken? 🏆\n\nDrop your thoughts 👇\n\n#Messi #Record #Football #Goals",
    "📌 RECORD | Real Madrid have won the Champions League 15 times. The most successful club in UCL history. 🏆\n\nCan anyone catch them? 👇\n\n#RealMadrid #UCL #ChampionsLeague #Record",
    "📌 RECORD | Cristiano Ronaldo is the all-time top scorer in international football with over 130 goals. 🇵🇹\n\nWill anyone ever beat this? 👇\n\n#Ronaldo #Portugal #Goals #Record #Football",

    # Fun facts
    "😱 DID YOU KNOW | The fastest goal in football history was scored after just 2.4 seconds! ⚡\n\nWould you have even noticed? 😂 Drop a reaction below 👇\n\n#Football #FunFacts #FootballTrivia",
    "😱 DID YOU KNOW | Brazil is the only country to have played in every single FIFA World Cup. 🇧🇷🌍\n\nDid you know this? Drop a 🇧🇷 below if you did!\n\n#Brazil #WorldCup #FIFA #FootballFacts",
    "😱 DID YOU KNOW | The Premier League ball travels at over 80mph when struck by top players. ⚡\n\nInsane right? 😱 Drop a reaction 👇\n\n#PremierLeague #Football #FunFacts",

    # Fan polls
    "📣 FAN POLL | Which is the best league in the world right now? 🌍\n\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League\n🇪🇸 La Liga\n🇩🇪 Bundesliga\n🇮🇹 Serie A\n\nDrop your pick below 👇\n\n#Football #BestLeague #FootballTalk #Poll",
    "📣 FAN POLL | Who is the best young player in the world right now? 🌟\n\n⭐ Yamal\n⭐ Bellingham\n⭐ Endrick\n⭐ Camavinga\n\nDrop your pick 👇\n\n#Football #YoungPlayers #NextGen #Poll",
    "📣 FAN POLL | What is the greatest goal you have ever seen? ⚽\n\nDrop the player and match below 👇\n\n#Football #GreatestGoals #FootballMoments #Poll",

    # World Cup 2026 hype
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

# Filler timing
last_filler_time = 0

# ── Helpers ───────────────────────────────────────────────────────
def football_get(path):
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    try:
        r = requests.get(f"{FOOTBALL_BASE}{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
    return None

def post_to_facebook(message):
    payload = {"message": message, "access_token": FB_TOKEN}
    r = requests.post(FB_POST_URL, data=payload, timeout=10)
    if r.status_code == 200:
        print(f"[POSTED] {message[:70]}...")
        return True
    else:
        print(f"[ERROR] FB post failed: {r.status_code} {r.text}")
        return False

def get_score(match):
    home = match["homeTeam"]["shortName"]
    away = match["awayTeam"]["shortName"]
    ft   = match["score"]["fullTime"]
    ht   = match["score"]["halfTime"]
    hs   = ft["home"] if ft["home"] is not None else (ht["home"] or 0)
    as_  = ft["away"] if ft["away"] is not None else (ht["away"] or 0)
    return home, away, hs, as_

def get_league_code(league_name):
    return next((c for c, n in LEAGUES.items() if n == league_name), "")

def get_hashtags(league_name):
    code = get_league_code(league_name)
    return LEAGUE_HASHTAGS.get(code, "#Football #LiveFootball")

def is_heavy_matchday(all_matches_today):
    """Heavy day = 5+ big matches or major leagues playing."""
    big_leagues = {"PL", "PD", "SA", "BL1", "FL1", "CL", "WC", "EC"}
    total = sum(len(m) for m in all_matches_today.values())
    has_big = any(c in big_leagues for c in all_matches_today)
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
        flag        = LEAGUE_FLAGS.get(league_code, "🏆")
        league_name = LEAGUES.get(league_code, "Football")

        # On heavy days only show big leagues
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
    key = f"{match_id}_lineup"
    if key in posted_lineups:
        return

    home    = match["homeTeam"]["shortName"]
    away    = match["awayTeam"]["shortName"]
    lineups = match.get("lineups", [])
    if len(lineups) < 2:
        return

    def format_players(lineup):
        players = lineup.get("startXI", [])
        return "\n".join(
            f"  {i+1}. {p.get('player',{}).get('name','')}"
            for i, p in enumerate(players)
        )

    flag     = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
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
    match_id        = match["id"]
    home, away, hs, as_ = get_score(match)
    flag            = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
    hashtags        = get_hashtags(league_name)

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
    match_id        = match["id"]
    home, away, hs, as_ = get_score(match)
    flag            = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
    hashtags        = get_hashtags(league_name)

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
    key = f"{match_id}_halftime"
    if key in posted_halftimes:
        return

    home = match["homeTeam"]["shortName"]
    away = match["awayTeam"]["shortName"]
    hs   = match["score"]["halfTime"]["home"] or 0
    as_  = match["score"]["halfTime"]["away"] or 0
    flag = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
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
    key = f"{match_id}_fulltime"
    if key in posted_ft:
        return

    home, away, hs, as_ = get_score(match)
    flag     = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
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

    # Post next fixture
    handle_next_fixture(match, league_name)

    # Generate reel
    create_and_post_reel(match, league_name)

# ── Next fixture ──────────────────────────────────────────────────
def handle_next_fixture(match, league_name):
    match_id = match["id"]
    key      = f"{match_id}_nextfixture"
    if key in posted_next_fixtures:
        return

    home     = match["homeTeam"]["shortName"]
    away     = match["awayTeam"]["shortName"]
    home_id  = match["homeTeam"].get("id", "")
    away_id  = match["awayTeam"].get("id", "")
    flag     = LEAGUE_FLAGS.get(get_league_code(league_name), "🏆")
    hashtags = get_hashtags(league_name)

    home_next = None
    away_next = None

    try:
        today     = datetime.utcnow().strftime("%Y-%m-%d")
        future    = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
        code      = get_league_code(league_name)
        if code:
            data  = football_get(
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

# ── Filler content for light matchdays ───────────────────────────
def handle_filler(has_live_matches):
    global last_filler_time
    if has_live_matches:
        return  # Never post filler during live matches

    now = time.time()
    if now - last_filler_time < 1800:  # 30 minutes between filler posts
        return

    # Find unposted filler
    available = [p for p in FILLER_POSTS
                 if p[:50] not in posted_filler]
    if not available:
        # Reset if all posted
        posted_filler.clear()
        available = FILLER_POSTS

    post = random.choice(available)
    if post_to_facebook(post):
        posted_filler.add(post[:50])
        last_filler_time = now
        save_state(posted_goals, posted_cards, posted_lineups, posted_halftimes,
                   posted_ft, posted_matchdays, posted_next_fixtures, posted_filler)
        print(f"[FILLER] Posted filler content.")

# ── Main loop ─────────────────────────────────────────────────────
matchday_posted_today = None

def check_matches():
    global matchday_posted_today
    today = datetime.utcnow().strftime("%Y-%m-%d")

    all_matches_today = {}

    # Check all league competitions
    for code in LEAGUES:
        data = football_get(
            f"/competitions/{code}/matches?dateFrom={today}&dateTo={today}"
        )
        if data:
            matches = data.get("matches", [])
            if matches:
                all_matches_today[code] = matches

    # Check general endpoint for internationals and friendlies
    intl_data = football_get(f"/matches?dateFrom={today}&dateTo={today}")
    if intl_data:
        for match in intl_data.get("matches", []):
            comp_code = match.get("competition", {}).get("code", "")
            if comp_code not in LEAGUES:
                if "INTL" not in all_matches_today:
                    all_matches_today["INTL"] = []
                    LEAGUES["INTL"]      = "International / Friendlies"
                    LEAGUE_FLAGS["INTL"] = "🌍"
                    LEAGUE_HASHTAGS["INTL"] = "#InternationalFootball #WorldCup2026"
                # Avoid duplicates
                existing_ids = {m["id"] for m in all_matches_today["INTL"]}
                if match["id"] not in existing_ids:
                    all_matches_today["INTL"].append(match)

    # Check if any matches are currently live
    has_live = any(
        m.get("status") in ("IN_PLAY", "PAUSED")
        for matches in all_matches_today.values()
        for m in matches
    )

    # Post matchday preview once per day
    if matchday_posted_today != today:
        handle_matchday_preview(all_matches_today)
        matchday_posted_today = today

    # Process each match
    for code, matches in all_matches_today.items():
        league_name = LEAGUES.get(code, "Football")
        for match in matches:
            status = match.get("status")

            # Lineups — 45 to 75 mins before kickoff
            if status in ("TIMED", "SCHEDULED"):
                kickoff_str = match.get("utcDate", "")
                if kickoff_str:
                    kickoff = datetime.strptime(kickoff_str, "%Y-%m-%dT%H:%M:%SZ")
                    now = datetime.utcnow()
                    if timedelta(minutes=45) <= kickoff - now <= timedelta(minutes=75):
                        handle_lineups(match, league_name)

            # Live events
            if status == "IN_PLAY":
                handle_goals(match, league_name)
                handle_red_cards(match, league_name)

            # Half time
            if status == "PAUSED":
                handle_halftime(match, league_name)

            # Full time
            if status == "FINISHED":
                handle_fulltime(match, league_name)

    # Filler on light/no matchdays when nothing is live
    if not has_live:
        handle_filler(has_live)

def run():
    print(f"{PAGE_NAME} Match Bot started...")
    print(f"Monitoring: {', '.join(list(LEAGUES.values())[:6])} + more")
    print("Posting: Matchday preview, Lineups, Goals + Assists,")
    print("         Red Cards, Half Time, Full Time, Next Fixture, Filler\n")

    while True:
        try:
            check_matches()
        except Exception as e:
            print(f"[ERROR] {e}")
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Checked. Waiting 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    run()
