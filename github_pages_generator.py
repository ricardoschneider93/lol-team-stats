# github_pages_generator.py
# Generiert statische HTML-Seite für GitHub Pages

import json
import os
from datetime import datetime
from typing import Dict

class GitHubPagesGenerator:
    """Erstellt eine schöne statische HTML-Seite für GitHub Pages"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_page(self, team_data: Dict, output_dir: str = "docs") -> str:
        """Generiert die HTML-Seite"""
        
        # Erstelle docs Verzeichnis für GitHub Pages
        os.makedirs(output_dir, exist_ok=True)
        
        # Sortiere Spieler nach Rank
        players = list(team_data.get('players', {}).items())
        players.sort(key=lambda x: self._get_rank_value(x[1]), reverse=True)
        
        # Generiere HTML
        html_content = self.template.format(
            team_name=team_data.get('team_name', 'LoL Team'),
            last_updated=team_data.get('last_updated', ''),
            players_html=self._generate_players_html(players),
            success_count=team_data.get('success_count', 0),
            total_players=team_data.get('total_players', 0),
            team_stats=self._generate_team_stats(players)
        )
        
        # Schreibe HTML-Datei
        html_file = os.path.join(output_dir, "index.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Schreibe JSON-Daten (für API-Zugriff)
        json_file = os.path.join(output_dir, "data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(team_data, f, indent=2, ensure_ascii=False)
        
        return html_file
    
    def _get_rank_value(self, player: Dict) -> int:
        """Konvertiert Rank zu numerischem Wert für Sortierung"""
        tier = player.get('tier', '').lower()
        lp = player.get('lp', 0)
        
        tier_values = {
            'challenger': 9000,
            'grandmaster': 8000,
            'master': 7000,
            'diamond': 6000,
            'emerald': 5000,
            'platinum': 4000,
            'gold': 3000,
            'silver': 2000,
            'bronze': 1000,
            'iron': 0
        }
        
        base_value = tier_values.get(tier, 0)
        return base_value + lp
    
    def _generate_players_html(self, players) -> str:
        """Generiert HTML für Spieler-Liste"""
        html_parts = []
        
        for riot_id, player in players:
            tier = player.get('tier', 'Unranked')
            rank = player.get('rank', tier)
            lp = player.get('lp', 0)
            wins = player.get('wins', 0)
            losses = player.get('losses', 0)
            wr = player.get('win_rate', 0)
            total_games = player.get('total_games', 0)
            
            # Tier-spezifische Styling
            tier_class = self._get_tier_class(tier)
            
            # Champion Stats
            champions_html = ""
            main_champs = player.get('main_champions', [])[:3]  # Top 3
            for champ in main_champs:
                champions_html += f"""
                <div class="champion-stat">
                    <span class="champ-name">{champ['name']}</span>
                    <span class="champ-games">{champ['games']}G</span>
                    <span class="champ-wr">{champ['win_rate']}%</span>
                </div>
                """
            
            player_html = f"""
            <div class="player-card {tier_class}">
                <div class="player-header">
                    <h3 class="player-name">{riot_id}</h3>
                    <div class="player-rank">
                        <span class="rank-text">{rank}</span>
                        <span class="lp-text">{lp} LP</span>
                    </div>
                </div>
                
                <div class="player-stats">
                    <div class="stat-group">
                        <div class="stat">
                            <span class="stat-label">Games</span>
                            <span class="stat-value">{total_games}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Win Rate</span>
                            <span class="stat-value win-rate">{wr}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">W/L</span>
                            <span class="stat-value">{wins}W {losses}L</span>
                        </div>
                    </div>
                    
                    <div class="main-champions">
                        <h4>Main Champions</h4>
                        <div class="champions-list">
                            {champions_html}
                        </div>
                    </div>
                </div>
            </div>
            """
            
            html_parts.append(player_html)
        
        return '\n'.join(html_parts)
    
    def _get_tier_class(self, tier: str) -> str:
        """Gibt CSS-Klasse für Tier zurück"""
        tier_lower = tier.lower()
        tier_classes = {
            'challenger': 'tier-challenger',
            'grandmaster': 'tier-grandmaster', 
            'master': 'tier-master',
            'diamond': 'tier-diamond',
            'emerald': 'tier-emerald',
            'platinum': 'tier-platinum',
            'gold': 'tier-gold',
            'silver': 'tier-silver',
            'bronze': 'tier-bronze',
            'iron': 'tier-iron'
        }
        return tier_classes.get(tier_lower, 'tier-unranked')
    
    def _generate_team_stats(self, players) -> str:
        """Generiert Team-Statistiken"""
        if not players:
            return "<p>Keine Spieler-Daten verfügbar</p>"
        
        total_games = sum(p[1].get('total_games', 0) for p in players)
        total_wins = sum(p[1].get('wins', 0) for p in players)
        avg_wr = round((total_wins / max(total_games, 1)) * 100)
        
        # Höchster Rank
        highest_player = max(players, key=lambda x: self._get_rank_value(x[1]))
        highest_rank = highest_player[1].get('rank', 'Unranked')
        
        return f"""
        <div class="team-stats">
            <div class="team-stat">
                <span class="stat-label">Team Games</span>
                <span class="stat-value">{total_games}</span>
            </div>
            <div class="team-stat">
                <span class="stat-label">Avg Win Rate</span>
                <span class="stat-value">{avg_wr}%</span>
            </div>
            <div class="team-stat">
                <span class="stat-label">Highest Rank</span>
                <span class="stat-value">{highest_rank}</span>
            </div>
        </div>
        """
    
    def _get_html_template(self) -> str:
        """HTML Template für die GitHub Pages Seite"""
        return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team_name} - LoL Team Stats</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .team-name {{
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #c89b3c, #f0e6d2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .last-updated {{
            color: #cdbe91;
            font-size: 1.1rem;
        }}
        
        .team-overview {{
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(200, 155, 60, 0.1);
            border-radius: 10px;
            border-left: 4px solid #c89b3c;
        }}
        
        .team-stats {{
            display: flex;
            gap: 30px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .team-stat {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }}
        
        .players-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .player-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .player-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        /* Tier-spezifische Farben */
        .tier-challenger {{ border-color: #f4c2a1; }}
        .tier-grandmaster {{ border-color: #ff6b6b; }}
        .tier-master {{ border-color: #a855f7; }}
        .tier-diamond {{ border-color: #3b82f6; }}
        .tier-emerald {{ border-color: #10b981; }}
        .tier-platinum {{ border-color: #14b8a6; }}
        .tier-gold {{ border-color: #f59e0b; }}
        .tier-silver {{ border-color: #6b7280; }}
        .tier-bronze {{ border-color: #92400e; }}
        .tier-iron {{ border-color: #374151; }}
        
        .player-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .player-name {{
            font-size: 1.3rem;
            color: #c89b3c;
        }}
        
        .player-rank {{
            text-align: right;
        }}
        
        .rank-text {{
            font-size: 1.1rem;
            font-weight: bold;
            display: block;
        }}
        
        .lp-text {{
            font-size: 0.9rem;
            color: #cdbe91;
        }}
        
        .stat-group {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            color: #cdbe91;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 1.1rem;
            font-weight: bold;
        }}
        
        .win-rate {{
            color: #10b981;
        }}
        
        .main-champions h4 {{
            font-size: 1rem;
            margin-bottom: 10px;
            color: #c89b3c;
        }}
        
        .champions-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .champion-stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        
        .champ-name {{
            font-weight: bold;
            flex: 1;
        }}
        
        .champ-games {{
            color: #cdbe91;
            font-size: 0.9rem;
        }}
        
        .champ-wr {{
            color: #10b981;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .success-info {{
            color: #10b981;
            font-size: 1.1rem;
        }}
        
        @media (max-width: 768px) {{
            .team-name {{
                font-size: 2rem;
            }}
            
            .players-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stat-group {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .team-stats {{
                flex-direction: column;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 class="team-name">{team_name}</h1>
            <p class="last-updated">Letztes Update: {last_updated}</p>
        </header>
        
        <section class="team-overview">
            <h2>📊 Team Übersicht</h2>
            {team_stats}
        </section>
        
        <main class="players-grid">
            {players_html}
        </main>
        
        <footer class="footer">
            <div class="success-info">
                ✅ {success_count}/{total_players} Spieler erfolgreich gescrapt
            </div>
            <p style="margin-top: 15px; color: #cdbe91;">
                🔄 Automatisch generiert • 💻 Powered by op.gg • 🌐 GitHub Pages
            </p>
        </footer>
    </div>
</body>
</html>"""
