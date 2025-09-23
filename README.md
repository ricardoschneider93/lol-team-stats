# LoL Team Stats - Vollautomatisch

🎮 **Ein Skript - alles online!**

## ⚡ SETUP (einmalig)

### 1. Token erstellen
1. **Gehe zu:** [github.com/settings/tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. **Scopes:** ✅ `repo` ankreuzen
4. **Token kopieren!**

### 2. Config ausfüllen
**Bearbeite `config.py`:**
```python
TEAM_CONFIG = {
    "team_name": "Dein Team Name",
    "players": {
        "SpielerName#1234": {"region": "euw1"},
        # Deine Spieler hier...
    }
}

GITHUB_CONFIG = {
    "username": "ricardoschneider93",    # Dein GitHub Username
    "repo_name": "lol-team-stats",       # Repository Name
    "token": "ghp_xxxxxxxxxxxx",         # DEIN TOKEN HIER!
}
```

---

## 🚀 ALLES AUTOMATISCH

**Ein Befehl - fertig:**
```bash
pip install -r requirements.txt
python main.py
```

**Das Skript macht automatisch:**
- ✅ Scraped deine Team-Stats
- ✅ Erstellt GitHub Repository  
- ✅ Lädt Code hoch
- ✅ Erstellt Website
- ✅ Zeigt dir die Live-URL

---

## 🔄 UPDATES

**Stats aktualisieren:**
```bash
python main.py
```

Fertig! Website aktualisiert sich automatisch.

---

## 🆘 Problem?

- **"Token fehlt"** → Token in config.py eintragen
- **"Keine Spieler"** → Riot IDs in config.py prüfen
- **Website lädt nicht** → 5 Minuten warten

---

**Das wars! Ein Skript, alles online! 🎯**