# main.py
# Vollautomatisches LoL Team Stats Tool - alles in einem Skript!

import logging
import sys
import os
from datetime import datetime

from lol_scraper import LoLScraper
from github_pages_generator import GitHubPagesGenerator
from github_manager import GitHubManager
from config import TEAM_CONFIG, GITHUB_CONFIG

def setup_logging():
    """Setup Logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_config():
    """Validiert Konfiguration"""
    logger = logging.getLogger(__name__)
    
    # Team-Konfiguration prüfen
    players = TEAM_CONFIG.get('players', {})
    if not players:
        logger.error("❌ Keine Spieler in config.py!")
        logger.error("➡️  Füge deine Spieler in TEAM_CONFIG hinzu")
        return False
    
    # GitHub-Konfiguration prüfen
    username = GITHUB_CONFIG.get('username', '')
    token = GITHUB_CONFIG.get('token', '')
    repo_name = GITHUB_CONFIG.get('repo_name', '')
    
    if not username:
        logger.error("❌ GitHub Username fehlt in config.py!")
        logger.error("➡️  Füge deinen Username in GITHUB_CONFIG hinzu")
        return False
    
    # Token wird jetzt sicher aus github_token.txt geladen, nicht aus config.py
    
    if not repo_name:
        logger.error("❌ Repository Name fehlt in config.py!")
        return False
    
    return True

def main():
    """Vollautomatischer Prozess - alles in einem!"""
    # Sicherstellen, dass wir im richtigen Verzeichnis sind
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    
    # 1. Konfiguration validieren
    if not validate_config():
        logger.error("🔧 Bitte korrigiere config.py und führe das Skript erneut aus")
        return False
    
    team_name = TEAM_CONFIG.get('team_name', 'LoL Team')
    players = list(TEAM_CONFIG.get('players', {}).keys())
    
    logger.info(f"🎯 Team: {team_name}")
    logger.info(f"👥 Spieler: {players}")
    
    try:
        # 2. Scrape Team-Daten
        logger.info("🔍 Scrape Team-Daten von op.gg...")
        scraper = LoLScraper()
        team_data = scraper.scrape_team(TEAM_CONFIG)
        
        if team_data['success_count'] == 0:
            logger.error("❌ Keine Spielerdaten erhalten!")
            return False
        
        # 3. Generiere GitHub Pages
        logger.info("🌐 Generiere Website...")
        generator = GitHubPagesGenerator()
        html_file = generator.generate_page(team_data)
        logger.info(f"✅ Website generiert: {html_file}")
        
        # 4. Automatischer GitHub Deployment
        username = GITHUB_CONFIG['username']
        repo_name = GITHUB_CONFIG['repo_name']
        
        # GitHub Token sicher laden (nicht aus versioniertem Code!)
        token_file = "github_token.txt"
        token = ""
        
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                if token and token != "HIER_IHREN_TOKEN_EINTRAGEN":
                    logger.info("🔑 GitHub Token sicher geladen")
                else:
                    logger.error("❌ Token in github_token.txt nicht konfiguriert!")
                    print(f"""
⚠️  GITHUB TOKEN SETUP ERFORDERLICH:

🔑 Erstelle neuen Token:
    1. https://github.com/settings/tokens
    2. "Generate new token (classic)"
    3. Scopes: ✓ repo ✓ workflow
    4. Token kopieren

💾 Token sicher speichern:
    Öffne: github_token.txt
    Inhalt: ghp_xxxxxxxxxxxxxxxxxxxx (nur das Token!)
    
💡 Warum so? GitHub deaktiviert Token die im Code stehen automatisch!
    """)
                    return False
            except Exception as e:
                logger.error(f"❌ Fehler beim Laden des Tokens: {e}")
                return False
        else:
            # Fallback: Token aus config.py (unsicher!)
            token = GITHUB_CONFIG.get('token', '').strip()
            if token and token != "HIER_NEUEN_TOKEN_EINTRAGEN":
                logger.warning("⚠️  Token aus config.py geladen - unsicher! Verwende github_token.txt")
            else:
                logger.error("❌ Kein GitHub Token gefunden!")
                print(f"""
⚠️  GITHUB TOKEN SETUP ERFORDERLICH:

🔑 Erstelle neuen Token:
    1. https://github.com/settings/tokens
    2. "Generate new token (classic)"  
    3. Scopes: ✓ repo ✓ workflow
    4. Token kopieren

💾 Token sicher speichern:
    Erstelle Datei: github_token.txt
    Inhalt: ghp_xxxxxxxxxxxxxxxxxxxx (nur das Token!)
    
💡 Warum so? GitHub deaktiviert Token die im Code stehen automatisch!
                """)
                return False
        
        logger.info("🚀 Starte automatischen GitHub Deployment...")
        github_manager = GitHubManager(username, token, repo_name)
        
        success, website_url = github_manager.full_deployment()
        
        if success:
            print(f"""

🎉 VOLLAUTOMATISCH ERFOLGREICH!
═══════════════════════════════

✅ Team-Daten gescraped: {team_data['success_count']}/{len(team_data['players'])} Spieler
✅ Professionelles Dashboard generiert
✅ Automatisch zu GitHub gepusht
✅ Live-Website: {website_url}

💡 Dashboard Features:
    📊 Grafana-Style Performance Dashboard
    🏆 Champion-Karten mit Icons & Stats
    📈 KDA, Damage, CS, Vision Analytics
    🎮 Recent Games & Trends

🌐 Teile diese URL mit deinem Team: {website_url}
            """)
        else:
            print(f"""

🎉 DASHBOARD ERFOLGREICH GENERIERT!
═══════════════════════════════════

✅ Team-Daten gescraped: {team_data['success_count']}/{len(team_data['players'])} Spieler  
✅ Professionelles Dashboard: docs/index.html
⚠️ GitHub Push fehlgeschlagen (Authentifizierung)

💡 Dashboard Features:
    📊 Grafana-Style Performance Dashboard
    🏆 Champion-Karten mit Icons & Stats  
    📈 KDA, Damage, CS, Vision Analytics
    🎮 Recent Games & Trends

🌐 Lokale Vorschau: Öffne docs/index.html im Browser
🔧 Für Auto-Push: Git-Authentifizierung konfigurieren
            """)
            return True  # Dashboard ist erfolgreich, auch ohne Push
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)