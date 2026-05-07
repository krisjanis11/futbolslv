import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "futbols_secret_2025"

# ── Database connection ──────────────────────────────────────────
def get_db():
    db = Path(__file__).parent / "futbols.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = Path(__file__).parent / "futbols.db"
    if db_path.exists():
        return
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leagues (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            country   TEXT NOT NULL,
            short_code TEXT NOT NULL,
            founded   INTEGER
        );

        CREATE TABLE IF NOT EXISTS teams (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            city      TEXT NOT NULL,
            stadium   TEXT,
            founded   INTEGER,
            league_id INTEGER NOT NULL,
            FOREIGN KEY (league_id) REFERENCES leagues(id)
        );

        CREATE TABLE IF NOT EXISTS players (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            nationality TEXT NOT NULL,
            position    TEXT NOT NULL,
            age         INTEGER,
            height_cm   INTEGER,
            market_value TEXT,
            biography   TEXT,
            team_id     INTEGER NOT NULL,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS player_stats (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id    INTEGER NOT NULL,
            season       TEXT DEFAULT '2024-25',
            appearances  INTEGER DEFAULT 0,
            goals        INTEGER DEFAULT 0,
            assists      INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES players(id)
        );

        -- Leagues
        INSERT INTO leagues (name, country, short_code, founded) VALUES
            ('Premier League', 'Anglija',  'PL', 1992),
            ('La Liga',        'Spānija',  'LL', 1929),
            ('Bundesliga',     'Vācija',   'BL', 1963);
        
        -- Teams — Premier League (20)
        INSERT INTO teams (name, city, stadium, founded, league_id) VALUES
            ('Arsenal',             'London',        'Emirates Stadium',            1886, 1),
            ('Aston Villa',         'Birmingham',    'Villa Park',                  1874, 1),
            ('Bournemouth',         'Bournemouth',   'Vitality Stadium',            1899, 1),
            ('Brentford',           'London',        'Gtech Community Stadium',     1889, 1),
            ('Brighton',            'Brighton',      'Amex Stadium',                1901, 1),
            ('Chelsea',             'London',        'Stamford Bridge',             1905, 1),
            ('Crystal Palace',      'London',        'Selhurst Park',               1905, 1),
            ('Everton',             'Liverpool',     'Goodison Park',               1878, 1),
            ('Fulham',              'London',        'Craven Cottage',              1879, 1),
            ('Ipswich Town',        'Ipswich',       'Portman Road',                1878, 1),
            ('Leicester City',      'Leicester',     'King Power Stadium',          1884, 1),
            ('Liverpool',           'Liverpool',     'Anfield',                     1892, 1),
            ('Manchester City',     'Manchester',    'Etihad Stadium',              1880, 1),
            ('Manchester United',   'Manchester',    'Old Trafford',                1878, 1),
            ('Newcastle',           'Newcastle',     'St. James Park',              1892, 1),
            ('Nottingham Forest',   'Nottingham',    'City Ground',                 1865, 1),
            ('Southampton',         'Southampton',   'St. Mary''s Stadium',         1885, 1),
            ('Tottenham',           'London',        'Tottenham Hotspur Stadium',   1882, 1),
            ('West Ham',            'London',        'London Stadium',              1895, 1),
            ('Wolves',              'Wolverhampton', 'Molineux',                    1877, 1),

        -- Teams — La Liga (20)
            ('Athletic Bilbao',     'Bilbao',        'San Mamés',                   1898, 2),
            ('Atletico Madrid',     'Madrid',        'Civitas Metropolitano',       1903, 2),
            ('Barcelona',           'Barcelona',     'Camp Nou',                    1899, 2),
            ('Celta Vigo',          'Vigo',          'Balaídos',                    1923, 2),
            ('Deportivo Alaves',    'Vitoria',       'Mendizorrotza',               1921, 2),
            ('Espanyol',            'Barcelona',     'RCDE Stadium',                1900, 2),
            ('Getafe',              'Getafe',        'Coliseum Alfonso Pérez',      1983, 2),
            ('Girona',              'Girona',        'Montilivi',                   1930, 2),
            ('Las Palmas',          'Las Palmas',    'Estadio Gran Canaria',        1949, 2),
            ('Leganes',             'Leganés',       'Estadio Municipal de Butarque',1928,2),
            ('Mallorca',            'Palma',         'Visit Mallorca Estadi',       1916, 2),
            ('Osasuna',             'Pamplona',      'El Sadar',                    1920, 2),
            ('Rayo Vallecano',      'Madrid',        'Estadio de Vallecas',         1924, 2),
            ('Real Betis',          'Seville',       'Benito Villamarín',           1907, 2),
            ('Real Madrid',         'Madrid',        'Santiago Bernabéu',           1902, 2),
            ('Real Sociedad',       'San Sebastián', 'Reale Arena',                 1909, 2),
            ('Real Valladolid',     'Valladolid',    'Estadio José Zorrilla',       1928, 2),
            ('Sevilla',             'Seville',       'Ramón Sánchez-Pizjuán',       1890, 2),
            ('Valencia',            'Valencia',      'Mestalla',                    1919, 2),
            ('Villarreal',          'Villarreal',    'Estadio de la Cerámica',      1923, 2),

        -- Teams — Bundesliga (18)
            ('Augsburg',            'Augsburg',      'WWK Arena',                   1907, 3),
            ('Bayern Munich',       'Munich',        'Allianz Arena',               1900, 3),
            ('Bayer Leverkusen',    'Leverkusen',    'BayArena',                    1904, 3),
            ('Borussia Dortmund',   'Dortmund',      'Signal Iduna Park',           1909, 3),
            ('B. Mönchengladbach',  'Mönchengladbach','Borussia-Park',              1900, 3),
            ('Eintracht Frankfurt', 'Frankfurt',     'Deutsche Bank Park',          1899, 3),
            ('Freiburg',            'Freiburg',      'Europa-Park Stadion',         1904, 3),
            ('Hamburg SV',          'Hamburg',       'Volksparkstadion',            1887, 3),
            ('Heidenheim',          'Heidenheim',    'Voith-Arena',                 1846, 3),
            ('Hoffenheim',          'Sinsheim',      'PreZero Arena',               1899, 3),
            ('Holstein Kiel',       'Kiel',          'Holstein-Stadion',            1900, 3),
            ('Mainz',               'Mainz',         'MEWA Arena',                  1905, 3),
            ('RB Leipzig',          'Leipzig',       'Red Bull Arena',              2009, 3),
            ('St. Pauli',           'Hamburg',       'Millerntor-Stadion',          1910, 3),
            ('Stuttgart',           'Stuttgart',     'MHPArena',                    1893, 3),
            ('Union Berlin',        'Berlin',        'Stadion An der Alten Försterei',1906,3),
            ('Werder Bremen',       'Bremen',        'Wohninvest Weserstadion',     1899, 3),
            ('Wolfsburg',           'Wolfsburg',     'Volkswagen Arena',            1945, 3);

        -- Players
        INSERT INTO players (name, nationality, position, age, height_cm, market_value, biography, team_id) VALUES
            ('Mohamed Salah',      'Ēģipte',    'Uzbrucējs', 32, 175, '€80m',  'Četru reižu Premier League "Zelta kurpes" ieguvējs. 2024-25 sezonā izcīnīja 29 vārtus un 18 piespēles.', (SELECT id FROM teams WHERE name='Liverpool')),
            ('Alexander Isak',     'Zviedrija', 'Uzbrucējs', 25, 190, '€100m', 'Elegants zviedru centrs ar izcilu vārtu gūšanas instinktu. 2024-25 sezonā ieguva 23 vārtus.', (SELECT id FROM teams WHERE name='Newcastle')),
            ('Bryan Mbeumo',       'Kamerūna',  'Uzbrucējs', 25, 171, '€70m',  'Brentford elektriskais spēlētājs ar 20 vārtiem un 7 piespēlēm 2024-25 sezonā.', (SELECT id FROM teams WHERE name='Brentford')),
            ('Erling Haaland',     'Norvēģija', 'Uzbrucējs', 24, 194, '€180m', 'Premier League rekordu lauzējs. 2024-25 sezonā ieguva 22 vārtus, neskatoties uz savainojumu.', (SELECT id FROM teams WHERE name='Manchester City')),
            ('Cole Palmer',        'Anglija',   'Pussargs',  22, 185, '€120m', 'Čelsijas radošais ģēnijs ar 15 vārtiem un 9 piespēlēm 2024-25 sezonā.', (SELECT id FROM teams WHERE name='Chelsea')),
            ('Bukayo Saka',        'Anglija',   'Uzbrucējs', 23, 178, '€150m', 'Arsenāla universālais angļu spārnspēlētājs ar 13 vārtiem un 11 piespēlēm.', (SELECT id FROM teams WHERE name='Arsenal')),
            ('Kylian Mbappé',      'Francija',  'Uzbrucējs', 26, 178, '€180m', 'Ieguva Pichichi balvu ar 31 vārtu La Liga, kā arī Eiropas Zelta kurpi 2024-25 sezonā.', (SELECT id FROM teams WHERE name='Real Madrid')),
            ('Robert Lewandowski', 'Polija',    'Uzbrucējs', 36, 185, '€15m',  'Polijas visu laiku labākais vārtu guvējs. 2024-25 sezonā ieguva 27 vārtus Barselonas krāsās.', (SELECT id FROM teams WHERE name='Barcelona')),
            ('Ante Budimir',       'Horvātija', 'Uzbrucējs', 33, 188, '€12m',  'Osasuna spēcīgais horvātu uzbrucējs ar 22 La Liga vārtiem 2024-25 sezonā.', (SELECT id FROM teams WHERE name='Osasuna')),
            ('Lamine Yamal',       'Spānija',   'Uzbrucējs', 17, 180, '€180m', 'Vispievilcīgākais pusaudzis pasaules futbolā – 10 vārti un 16 piespēles 35 mačos.', (SELECT id FROM teams WHERE name='Barcelona')),
            ('Harry Kane',         'Anglija',   'Uzbrucējs', 31, 188, '€60m',  'Anglijas kapteinis izcīnīja otro Torjägerkanone pēc kārtas ar 26 Bundesligas vārtiem.', (SELECT id FROM teams WHERE name='Bayern Munich')),
            ('Michael Olise',      'Francija',  'Uzbrucējs', 23, 181, '€80m',  'Francijas sprādzienbīstamais spārnspēlētājs – Bundesligas piespēļu līderis ar 15 piespēlēm.', (SELECT id FROM teams WHERE name='Bayern Munich')),
            ('Florian Wirtz',      'Vācija',    'Pussargs',  22, 180, '€130m', 'Vācijas izcilākais jaunais spēlētājs ar 11 vārtiem un 12 piespēlēm Leverkusenā.', (SELECT id FROM teams WHERE name='Bayer Leverkusen')),
            ('Jonathan Burkardt',  'Vācija',    'Uzbrucējs', 24, 185, '€22m',  'Minca uzlecošā zvaigzne ar 18 Bundesligas vārtiem – labākā sezona karjerā.', (SELECT id FROM teams WHERE name='Mainz'));

        -- Player stats (2024-25)
        INSERT INTO player_stats (player_id, appearances, goals, assists, yellow_cards) VALUES
            (1,  38, 29, 18, 1),
            (2,  35, 23,  4, 2),
            (3,  38, 20,  7, 3),
            (4,  31, 22,  5, 1),
            (5,  35, 15,  9, 2),
            (6,  37, 13, 11, 2),
            (7,  34, 31,  9, 3),
            (8,  35, 27,  8, 1),
            (9,  36, 22,  3, 4),
            (10, 35, 10, 16, 1),
            (11, 29, 26,  8, 2),
            (12, 27, 13, 15, 1),
            (13, 30, 11, 12, 2),
            (14, 32, 18,  4, 4);
    """)
    conn.commit()
    conn.close()
    
# ── ROUTES ──────────────────────────────────────────────────────

# 1. Sākumlapa
@app.route("/")
def index():
    conn = get_db()
    # Stats for hero section
    total_players = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    total_teams   = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    total_goals   = conn.execute("SELECT SUM(goals) FROM player_stats").fetchone()[0]
    # Top 3 scorers for homepage
    top3 = conn.execute("""
        SELECT players.name, players.nationality, players.position,
               teams.name AS team, leagues.short_code AS league,
               player_stats.goals, player_stats.assists
        FROM player_stats
        JOIN players ON player_stats.player_id = players.id
        JOIN teams   ON players.team_id = teams.id
        JOIN leagues ON teams.league_id = leagues.id
        ORDER BY player_stats.goals DESC LIMIT 3
    """).fetchall()
    conn.close()
    return render_template("index.html",
                           total_players=total_players,
                           total_teams=total_teams,
                           total_goals=total_goals,
                           top3=top3)
    
# 2. Spēlētāji — saraksts
@app.route("/speletaji")
def players():
    conn = get_db()
    league_filter = request.args.get("liga", "")
    search = request.args.get("meklet", "")

    query = """
        SELECT players.*, teams.name AS team, leagues.short_code AS league,
               leagues.name AS league_name,
               player_stats.goals, player_stats.assists, player_stats.appearances
        FROM players
        JOIN teams   ON players.team_id  = teams.id
        JOIN leagues ON teams.league_id  = leagues.id
        LEFT JOIN player_stats ON player_stats.player_id = players.id
        WHERE 1=1
    """
    params = []
    if league_filter:
        query += " AND leagues.short_code = ?"
        params.append(league_filter)
    if search:
        query += " AND (players.name LIKE ? OR teams.name LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    query += " ORDER BY player_stats.goals DESC"

    all_players = conn.execute(query, params).fetchall()
    leagues = conn.execute("SELECT * FROM leagues").fetchall()
    conn.close()
    return render_template("players.html", players=all_players,
                           leagues=leagues, league_filter=league_filter, search=search)

# 3. Spēlētāja profils
@app.route("/speletaji/<int:player_id>")
def player_show(player_id):
    conn = get_db()
    player = conn.execute("""
        SELECT players.*, teams.name AS team, teams.city, teams.stadium,
               leagues.name AS league, leagues.short_code AS league_code,
               player_stats.goals, player_stats.assists,
               player_stats.appearances, player_stats.yellow_cards, player_stats.season
        FROM players
        JOIN teams   ON players.team_id  = teams.id
        JOIN leagues ON teams.league_id  = leagues.id
        LEFT JOIN player_stats ON player_stats.player_id = players.id
        WHERE players.id = ?
    """, (player_id,)).fetchone()
    conn.close()
    if not player:
        flash("Spēlētājs nav atrasts.", "error")
        return redirect(url_for("players"))
    return render_template("player_show.html", player=player)

# 4. Līgas
@app.route("/ligas")
def leagues():
    conn = get_db()
    all_leagues = conn.execute("""
        SELECT leagues.*,
               COUNT(DISTINCT teams.id) AS team_count,
               COUNT(DISTINCT players.id) AS player_count
        FROM leagues
        LEFT JOIN teams   ON teams.league_id  = leagues.id
        LEFT JOIN players ON players.team_id  = teams.id
        GROUP BY leagues.id
    """).fetchall()
    conn.close()
    return render_template("leagues.html", leagues=all_leagues)

# 5. Liga — detaļas ar komandām un spēlētājiem
@app.route("/ligas/<int:league_id>")
def league_show(league_id):
    conn = get_db()
    league = conn.execute("SELECT * FROM leagues WHERE id=?", (league_id,)).fetchone()
    teams  = conn.execute("SELECT * FROM teams WHERE league_id=? ORDER BY name", (league_id,)).fetchall()
    top_scorers = conn.execute("""
        SELECT players.name, players.nationality, teams.name AS team,
               player_stats.goals, player_stats.assists, player_stats.appearances
        FROM player_stats
        JOIN players ON player_stats.player_id = players.id
        JOIN teams   ON players.team_id = teams.id
        WHERE teams.league_id = ?
        ORDER BY player_stats.goals DESC LIMIT 5
    """, (league_id,)).fetchall()
    conn.close()
    if not league:
        return redirect(url_for("leagues"))
    return render_template("league_show.html", league=league, teams=teams, top_scorers=top_scorers)

# 6.CREATE — forma jauna spēlētāja pievienošanai
@app.route("/admin/speletaji/jauns", methods=["GET", "POST"])
def player_create():
    conn = get_db()
    if request.method == "POST":
        name        = request.form["name"].strip()
        nationality = request.form["nationality"].strip()
        position    = request.form["position"].strip()
        age         = request.form.get("age", 0)
        height_cm   = request.form.get("height_cm", 0)
        market_value= request.form.get("market_value", "").strip()
        biography   = request.form.get("biography", "").strip()
        team_id     = request.form["team_id"]

        if not name or not nationality or not position or not team_id:
            flash("Lūdzu aizpildi visus obligātos laukus!", "error")
        else:
            conn.execute("""
                INSERT INTO players (name, nationality, position, age, height_cm, market_value, biography, team_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, nationality, position, age, height_cm, market_value, biography, team_id))
            conn.commit()

            # Add empty stats row for new player
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute("INSERT INTO player_stats (player_id) VALUES (?)", (new_id,))
            conn.commit()
            conn.close()
            flash(f'Spēlētājs "{name}" veiksmīgi pievienots!', "success")
            return redirect(url_for("players"))

    teams = conn.execute("""
        SELECT teams.id, teams.name, leagues.short_code
        FROM teams JOIN leagues ON teams.league_id = leagues.id ORDER BY leagues.id, teams.name
    """).fetchall()
    conn.close()
    return render_template("player_form.html", player=None, teams=teams, action="Pievienot")


# 7. UPDATE — rediģēšanas forma
@app.route("/admin/speletaji/<int:player_id>/redaktet", methods=["GET", "POST"])
def player_edit(player_id):
    conn = get_db()
    player = conn.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone()
    if not player:
        conn.close()
        flash("Spēlētājs nav atrasts.", "error")
        return redirect(url_for("players"))

    if request.method == "POST":
        name        = request.form["name"].strip()
        nationality = request.form["nationality"].strip()
        position    = request.form["position"].strip()
        age         = request.form.get("age", 0)
        height_cm   = request.form.get("height_cm", 0)
        market_value= request.form.get("market_value", "").strip()
        biography   = request.form.get("biography", "").strip()
        team_id     = request.form["team_id"]

        if not name or not nationality or not position or not team_id:
            flash("Lūdzu aizpildi visus obligātos laukus!", "error")
        else:
            conn.execute("""
                UPDATE players SET name=?, nationality=?, position=?, age=?,
                height_cm=?, market_value=?, biography=?, team_id=? WHERE id=?
            """, (name, nationality, position, age, height_cm, market_value, biography, team_id, player_id))
            conn.commit()
            conn.close()
            flash(f'Spēlētājs "{name}" veiksmīgi atjaunināts!', "success")
            return redirect(url_for("player_show", player_id=player_id))

    teams = conn.execute("""
        SELECT teams.id, teams.name, leagues.short_code
        FROM teams JOIN leagues ON teams.league_id = leagues.id ORDER BY leagues.id, teams.name
    """).fetchall()
    conn.close()
    return render_template("player_form.html", player=player, teams=teams, action="Saglabāt")


# 8. DELETE — dzēšana
@app.route("/admin/speletaji/<int:player_id>/dzest", methods=["POST"])
def player_delete(player_id):
    conn = get_db()
    player = conn.execute("SELECT name FROM players WHERE id=?", (player_id,)).fetchone()
    if player:
        conn.execute("DELETE FROM player_stats WHERE player_id=?", (player_id,))
        conn.execute("DELETE FROM players WHERE id=?", (player_id,))
        conn.commit()
        flash(f'Spēlētājs "{player["name"]}" dzēsts.', "success")
    conn.close()
    return redirect(url_for("players"))


# 9. Admin panelis
@app.route("/admin")
def admin():
    conn = get_db()
    players_list = conn.execute("""
        SELECT players.id, players.name, players.position, players.nationality,
               teams.name AS team, leagues.short_code AS league
        FROM players
        JOIN teams   ON players.team_id  = teams.id
        JOIN leagues ON teams.league_id  = leagues.id
        ORDER BY players.name
    """).fetchall()
    conn.close()
    return render_template("admin.html", players=players_list)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)