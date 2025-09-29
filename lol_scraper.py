# lol_scraper.py
# Einfacher LoL Stats Scraper nur mit op.gg

import requests
import json
import logging
import re
import time
import urllib3
from urllib.parse import quote
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class LoLScraper:
    """Sammelt LoL Team-Daten von op.gg - einfach und zuverlässig"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # SSL-Konfiguration für Scraping
        self.session.verify = False  # SSL-Verifikation deaktivieren für Scraping
        
        # Warnungen für unsichere Requests unterdrücken
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Standard Browser Headers (ohne problematische Encoding-Header)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Region Mapping: Riot API -> op.gg
        self.region_map = {
            'euw1': 'euw', 'eun1': 'eune', 'na1': 'na', 'kr': 'kr',
            'jp1': 'jp', 'br1': 'br', 'la1': 'lan', 'la2': 'las',
            'oc1': 'oce', 'tr1': 'tr', 'ru': 'ru'
        }
    
    def get_player_stats(self, riot_id: str, region: str = "euw") -> Optional[Dict]:
        """Holt Spieler-Stats von op.gg"""
        try:
            if '#' not in riot_id:
                self.logger.error(f"Ungültiges Riot ID Format: {riot_id} (benötigt: Name#Tag)")
                return None
            
            game_name, tag_line = riot_id.split('#', 1)
            opgg_region = self.region_map.get(region.lower(), region.lower())
            
            # URL erstellen mit proper encoding
            encoded_name = quote(game_name)
            encoded_tag = quote(tag_line)
            url = f"https://op.gg/lol/summoners/{opgg_region}/{encoded_name}-{encoded_tag}"
            
            self.logger.info(f"🔍 Scraping {riot_id}...")
            
            # Request mit Retry-Logik
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, timeout=30, allow_redirects=True)
                    if response.status_code == 200:
                        break
                    elif response.status_code == 404:
                        self.logger.error(f"❌ Spieler {riot_id} nicht gefunden (404)")
                        return None
                    else:
                        self.logger.warning(f"⚠️  Versuch {attempt + 1}: Status {response.status_code} für {riot_id}")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Kurze Pause vor Retry
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"⚠️  Versuch {attempt + 1} fehlgeschlagen für {riot_id}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Kurze Pause vor Retry
                    else:
                        raise  # Re-raise nach letztem Versuch
            
            if response.status_code != 200:
                self.logger.error(f"❌ Fehler {response.status_code} für {riot_id} nach {max_retries} Versuchen")
                return None
            
            # Parse HTML mit korrektem Encoding
            response.encoding = 'utf-8'  # Force UTF-8 encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrahiere Daten aus Meta-Tags (zuverlässigste Methode)
            stats = self._extract_player_data(soup, riot_id)
            
            # Debug: Log extracted data
            if stats.get('tier') != 'Unranked':
                self.logger.debug(f"Extracted: {riot_id} -> {stats.get('tier')} {stats.get('rank')} {stats.get('lp')}LP, Champions: {len(stats.get('main_champions', []))}")
            
            if stats and stats.get('summoner_name'):
                self.logger.info(f"✅ {riot_id}: {stats.get('tier', 'Unknown')} - {stats.get('win_rate', 0)}% WR")
                return stats
            else:
                self.logger.error(f"❌ Keine Daten für {riot_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei {riot_id}: {e}")
            return None
    
    def _extract_player_data(self, soup: BeautifulSoup, riot_id: str) -> Dict:
        """Extrahiert Spielerdaten aus HTML - robuste Methode"""
        data = {
            'riot_id': riot_id,
            'summoner_name': riot_id,
            'tier': 'Unranked',
            'rank': '',
            'lp': 0,
            'wins': 0,
            'losses': 0,
            'total_games': 0,
            'win_rate': 0,
            'main_champions': [],
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Methode 1: Description Meta-Tag (Hauptdatenquelle)
            desc_meta = soup.find('meta', {'name': 'description'})
            if desc_meta:
                desc = desc_meta.get('content', '')
                self.logger.debug(f"Meta description found: {desc}")
            else:
                self.logger.debug("Description meta tag NOT FOUND - trying alternatives")
                # Versuche andere Meta-Tags
                twitter_desc = soup.find('meta', {'name': 'twitter:description'})
                if twitter_desc:
                    desc = twitter_desc.get('content', '')
                    self.logger.debug(f"Twitter description found: {desc}")
                else:
                    og_desc = soup.find('meta', {'property': 'og:description'})
                    if og_desc:
                        desc = og_desc.get('content', '')
                        self.logger.debug(f"OG Description found: {desc}")
                    else:
                        self.logger.debug("No description meta tags found")
                        desc = ""
            
            if desc:
                # Parse Tier/Rank - Unterstützt alle Tiers inklusive Master/Grandmaster/Challenger
                # Pattern Beispiele:
                # "Figure09#1893 / Platinum 1 1 39LP" - Tier mit Division und LP
                # "cl1ck9r#EUWES / Master 1 47LP" - Master+ Tier 
                tier_patterns = [
                    r'(Master|Grandmaster|Challenger)\s+\d+\s+(\d+)\s*LP',  # Master+ Format
                    r'(Iron|Bronze|Silver|Gold|Platinum|Diamond|Emerald)\s+(\d+)\s+\d+\s+(\d+)\s*LP',  # Mit Division, z.B. "Platinum 1 1 39LP"
                    r'(Iron|Bronze|Silver|Gold|Platinum|Diamond|Emerald)\s+(\d+)\s+(\d+)\s*LP',  # Einfaches Format, z.B. "Gold 3 45LP"
                ]
                
                for pattern in tier_patterns:
                    match = re.search(pattern, desc, re.IGNORECASE)
                    if match:
                        tier = match.group(1).lower()
                        if tier in ['master', 'grandmaster', 'challenger']:  # Master+ Tiers
                            data['tier'] = tier.title()
                            data['rank'] = tier.title()
                            data['lp'] = int(match.group(2))
                        else:  # Tier mit Division
                            division = match.group(2)
                            lp = int(match.group(3))
                            data['tier'] = tier.title()
                            data['rank'] = f"{tier.title()} {division}"
                            data['lp'] = lp
                        break
                
                # Parse Win/Loss
                wl_match = re.search(r'(\d+)Win\s+(\d+)Lose', desc)
                if wl_match:
                    wins = int(wl_match.group(1))
                    losses = int(wl_match.group(2))
                    data['wins'] = wins
                    data['losses'] = losses
                    data['total_games'] = wins + losses
                    data['win_rate'] = round((wins / (wins + losses)) * 100) if (wins + losses) > 0 else 0
                
                # Parse Champion Stats (aus der Description)
                # Pattern: "Urgot - 31Win 32Lose Win rate 49%"
                champions = []
                champ_matches = re.findall(r'([A-Za-z\'\.\s&]+)\s*-\s*(\d+)Win\s+(\d+)Lose\s+Win\s+rate\s+(\d+)%', desc)
                for champ_name, champ_wins, champ_losses, champ_wr in champ_matches:
                    champions.append({
                        'name': champ_name.strip(),
                        'wins': int(champ_wins),
                        'losses': int(champ_losses),
                        'games': int(champ_wins) + int(champ_losses),
                        'win_rate': int(champ_wr)
                    })
                
                data['main_champions'] = champions[:5]  # Top 5
            else:
                self.logger.warning(f"Keine Meta-Beschreibung gefunden für {riot_id}")
            
            return data
            
        except Exception as e:
            self.logger.warning(f"Parsing Fehler: {e}")
            return data
    
    def scrape_team(self, team_config: Dict[str, Dict]) -> Dict:
        """Scraped alle Team-Mitglieder"""
        team_data = {
            'team_name': team_config.get('team_name', 'LoL Team'),
            'players': {},
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_players': len(team_config.get('players', {}))
        }
        
        players = team_config.get('players', {})
        self.logger.info(f"🎮 Scraping {len(players)} Spieler...")
        
        success_count = 0
        for riot_id, player_config in players.items():
            region = player_config.get('region', 'euw1')
            
            player_data = self.get_player_stats(riot_id, region)
            if player_data:
                team_data['players'][riot_id] = player_data
                success_count += 1
            
            # Höfliche Pause zwischen Requests
            time.sleep(1)
        
        team_data['success_count'] = success_count
        self.logger.info(f"🎯 Scraping abgeschlossen: {success_count}/{len(players)} Spieler")
        
        return team_data
