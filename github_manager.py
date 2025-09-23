# github_manager.py
# Automatische GitHub Repository Verwaltung

import requests
import subprocess
import os
import logging
from typing import Dict, Tuple

class GitHubManager:
    """Automatische GitHub Repository Erstellung und Verwaltung"""
    
    def __init__(self, username: str, token: str, repo_name: str):
        self.username = username
        self.token = token
        self.repo_name = repo_name
        self.logger = logging.getLogger(__name__)
        
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def create_repository(self) -> bool:
        """Erstellt GitHub Repository automatisch"""
        try:
            # Prüfe ob Repository bereits existiert
            check_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}"
            check_response = requests.get(check_url, headers=self.headers)
            
            if check_response.status_code == 200:
                self.logger.info(f"✅ Repository {self.repo_name} existiert bereits")
                return True
            
            # Repository erstellen
            create_url = "https://api.github.com/user/repos"
            repo_data = {
                "name": self.repo_name,
                "description": "LoL Team Stats with GitHub Pages",
                "private": False,  # Public für GitHub Pages
                "has_issues": True,
                "has_projects": False,
                "has_wiki": False
            }
            
            self.logger.info(f"🔧 Erstelle Repository {self.repo_name}...")
            response = requests.post(create_url, json=repo_data, headers=self.headers)
            
            if response.status_code == 201:
                self.logger.info(f"✅ Repository {self.repo_name} erfolgreich erstellt!")
                return True
            else:
                self.logger.error(f"❌ Repository Erstellung fehlgeschlagen: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Repository Erstellung: {e}")
            return False
    
    def setup_local_git(self) -> bool:
        """Konfiguriert lokales Git Repository"""
        try:
            # Git init (falls noch nicht gemacht)
            if not os.path.exists('.git'):
                subprocess.run(['git', 'init'], check=True, capture_output=True)
                self.logger.info("🔧 Git Repository initialisiert")
            
            # Branch auf main setzen
            subprocess.run(['git', 'branch', '-M', 'main'], check=True, capture_output=True)
            
            # Remote hinzufügen/aktualisieren
            repo_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"
            
            try:
                subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
            except:
                pass  # Remote existiert noch nicht
            
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True, capture_output=True)
            self.logger.info("🔧 Git Remote konfiguriert")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Git Setup fehlgeschlagen: {e}")
            return False
    
    def push_to_github(self) -> bool:
        """Pushed Code zu GitHub"""
        try:
            # Alle Dateien hinzufügen
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            
            # Commit (nur wenn es Änderungen gibt)
            try:
                result = subprocess.run(['git', 'commit', '-m', 'Update LoL Team Stats'], 
                                      check=True, capture_output=True, text=True)
                self.logger.info("🔧 Änderungen committed")
            except subprocess.CalledProcessError:
                # Keine Änderungen zu committen
                self.logger.info("ℹ️  Keine neuen Änderungen zu committen")
            
            # Push zu GitHub
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True, capture_output=True)
            self.logger.info("✅ Code erfolgreich zu GitHub gepusht!")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ GitHub Push fehlgeschlagen: {e}")
            return False
    
    def enable_github_pages(self) -> Tuple[bool, str]:
        """Versucht GitHub Pages zu aktivieren (API noch in Beta)"""
        try:
            pages_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/pages"
            pages_data = {
                "source": {
                    "branch": "main",
                    "path": "/docs"
                }
            }
            
            # Prüfe ob Pages bereits aktiviert
            check_response = requests.get(pages_url, headers=self.headers)
            if check_response.status_code == 200:
                pages_info = check_response.json()
                url = pages_info.get('html_url', f"https://{self.username}.github.io/{self.repo_name}/")
                self.logger.info(f"✅ GitHub Pages bereits aktiv: {url}")
                return True, url
            
            # Versuche Pages zu aktivieren
            response = requests.post(pages_url, json=pages_data, headers=self.headers)
            
            if response.status_code in [201, 200]:
                pages_info = response.json()
                url = pages_info.get('html_url', f"https://{self.username}.github.io/{self.repo_name}/")
                self.logger.info(f"✅ GitHub Pages aktiviert: {url}")
                return True, url
            else:
                # API fehlgeschlagen - manuelle Aktivierung nötig
                url = f"https://{self.username}.github.io/{self.repo_name}/"
                self.logger.warning("⚠️  GitHub Pages API nicht verfügbar - manuelle Aktivierung nötig")
                return False, url
                
        except Exception as e:
            self.logger.error(f"❌ GitHub Pages Setup Fehler: {e}")
            url = f"https://{self.username}.github.io/{self.repo_name}/"
            return False, url
    
    def full_deployment(self) -> Tuple[bool, str]:
        """Kompletter automatischer Deployment-Prozess"""
        try:
            # 1. Repository erstellen
            if not self.create_repository():
                return False, ""
            
            # 2. Git Setup
            if not self.setup_local_git():
                return False, ""
            
            # 3. Push zu GitHub
            if not self.push_to_github():
                return False, ""
            
            # 4. GitHub Pages aktivieren
            pages_success, url = self.enable_github_pages()
            
            return True, url
            
        except Exception as e:
            self.logger.error(f"❌ Deployment fehlgeschlagen: {e}")
            return False, ""
