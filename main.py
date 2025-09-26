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
    
    if not token:
        logger.error("❌ GitHub Token fehlt in config.py!")
        logger.error("➡️  Erstelle einen Token und füge ihn in GITHUB_CONFIG hinzu")
        logger.error("     https://github.com/settings/tokens")
        return False
    
    if not repo_name:
        logger.error("❌ Repository Name fehlt in config.py!")
        return False
    
    return True

def main():
    """Vollautomatischer Prozess - alles in einem!"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("""
    ╔══════════════════════════════════════╗
    ║   LoL Team Stats - VOLLAUTOMATISCH   ║
    ║        🤖 Alles in einem Skript      ║
    ╚══════════════════════════════════════╝
    """)
    
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
        token = GITHUB_CONFIG['token']
        repo_name = GITHUB_CONFIG['repo_name']
        
        logger.info("🚀 Starte automatischen GitHub Deployment...")
        github_manager = GitHubManager(username, token, repo_name)
        
        success, website_url = github_manager.full_deployment()
        
        if success:
            print("Teile diese URL mit deinem Team: {website_url}")      
        else:
            logger.error("❌ GitHub Deployment fehlgeschlagen!")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)