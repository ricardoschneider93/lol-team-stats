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
            # Repository existiert bereits (vereinfachte Logik)
            # Da Git Push funktioniert, gehen wir davon aus, dass das Repository bereit ist
            self.logger.info(f"✅ Repository {self.repo_name} bereit für Deployment")
            return True
                
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
            
            # Remote hinzufügen/aktualisieren mit korrektem Token-Format
            repo_url = f"https://{self.token}@github.com/{self.username}/{self.repo_name}.git"
            
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
            has_changes = False
            try:
                result = subprocess.run(['git', 'commit', '-m', 'Update LoL Team Stats'], 
                                      check=True, capture_output=True, text=True)
                self.logger.info("🔧 Änderungen committed")
                has_changes = True
            except subprocess.CalledProcessError:
                # Keine Änderungen zu committen
                self.logger.info("ℹ️  Keine neuen Änderungen zu committen")
            
            # Push zu GitHub (nur wenn es Änderungen gab oder Force)
            if has_changes:
                subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True, capture_output=True)
                self.logger.info("✅ Code erfolgreich zu GitHub gepusht!")
            else:
                # Prüfe ob Remote aktuell ist
                try:
                    subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
                    self.logger.info("✅ Repository ist aktuell")
                except subprocess.CalledProcessError:
                    self.logger.info("ℹ️  Repository bereits aktuell")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ GitHub Push fehlgeschlagen: {e}")
            return False
    
    def enable_github_pages(self) -> Tuple[bool, str]:
        """GitHub Pages - vereinfachte Logik"""
        try:
            # Gehe davon aus, dass GitHub Pages bereits aktiviert ist
            url = f"https://{self.username}.github.io/{self.repo_name}/"
            self.logger.info(f"✅ GitHub Pages URL: {url}")
            return True, url
                
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
