#!/usr/bin/env python3
"""
Clash Royale Battle Analyzer for GitHub Pages
Lightweight version optimized for GitHub Actions
"""

import sqlite3
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import time

class ClashRoyaleAnalyzer:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.db_path = "clash_royale.db"
        self.base_url = "https://api.clashroyale.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_tag TEXT PRIMARY KEY,
                name TEXT,
                trophies INTEGER,
                best_trophies INTEGER,
                level INTEGER,
                clan_tag TEXT,
                clan_name TEXT,
                last_updated TEXT
            )
        """)
        
        # Battles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS battles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_tag TEXT,
                battle_time TEXT,
                battle_type TEXT,
                game_mode TEXT,
                is_ladder_tournament BOOLEAN,
                arena_id INTEGER,
                arena_name TEXT,
                result TEXT,
                crowns INTEGER,
                king_tower_hit_points INTEGER,
                princess_towers_hit_points TEXT,
                deck_cards TEXT,
                opponent_tag TEXT,
                opponent_name TEXT,
                opponent_trophies INTEGER,
                opponent_deck_cards TEXT,
                trophy_change INTEGER,
                FOREIGN KEY (player_tag) REFERENCES players (player_tag),
                UNIQUE(player_tag, battle_time, battle_type, game_mode)
            )
        """)
        
        # Clan members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clan_members (
                player_tag TEXT PRIMARY KEY,
                name TEXT,
                role TEXT,
                level INTEGER,
                trophies INTEGER,
                donations INTEGER,
                donations_received INTEGER,
                clan_tag TEXT,
                clan_name TEXT,
                last_seen TEXT,
                last_updated TEXT
            )
        """)
        
        # Deck performance view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS deck_performance AS
            SELECT 
                deck_cards,
                COUNT(*) as total_battles,
                SUM(CASE WHEN result = 'victory' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'defeat' THEN 1 ELSE 0 END) as losses,
                ROUND(AVG(CASE WHEN result = 'victory' THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
                SUM(COALESCE(trophy_change, 0)) as total_trophy_change,
                ROUND(AVG(COALESCE(trophy_change, 0)), 2) as avg_trophy_change,
                ROUND(AVG(crowns), 2) as avg_crowns
            FROM battles 
            WHERE deck_cards IS NOT NULL
            GROUP BY deck_cards
            ORDER BY win_rate DESC, total_battles DESC
        """)
        
        conn.commit()
        conn.close()
    
    def get_player_info(self, player_tag: str) -> Optional[Dict]:
        """Fetch player information from API"""
        clean_tag = player_tag.replace('#', '')
        url = f"{self.base_url}/players/%23{clean_tag}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching player info: {e}")
            return None
    
    def get_battle_log(self, player_tag: str) -> Optional[List[Dict]]:
        """Fetch player's battle log from API"""
        clean_tag = player_tag.replace('#', '')
        url = f"{self.base_url}/players/%23{clean_tag}/battlelog"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching battle log: {e}")
            return None
    
    def get_clan_info(self, clan_tag: str) -> Optional[Dict]:
        """Fetch clan information from API"""
        clean_tag = clan_tag.replace('#', '')
        url = f"{self.base_url}/clans/%23{clean_tag}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching clan info: {e}")
            return None
    
    def save_player_info(self, player_data: Dict):
        """Save player information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        clan_info = player_data.get('clan', {})
        
        cursor.execute("""
            INSERT OR REPLACE INTO players 
            (player_tag, name, trophies, best_trophies, level, clan_tag, clan_name, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_data['tag'],
            player_data['name'],
            player_data.get('trophies', 0),
            player_data.get('bestTrophies', 0),
            player_data.get('expLevel', 0),
            clan_info.get('tag'),
            clan_info.get('name'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_clan_members(self, clan_data: Dict):
        """Save clan member information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        clan_tag = clan_data['tag']
        clan_name = clan_data['name']
        
        for member in clan_data.get('memberList', []):
            cursor.execute("""
                INSERT OR REPLACE INTO clan_members 
                (player_tag, name, role, level, trophies, donations, donations_received, 
                 clan_tag, clan_name, last_seen, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member['tag'],
                member['name'],
                member['role'],
                member.get('expLevel', 0),
                member.get('trophies', 0),
                member.get('donations', 0),
                member.get('donationsReceived', 0),
                clan_tag,
                clan_name,
                member.get('lastSeen'),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def format_deck(self, cards: List[Dict]) -> str:
        """Format deck cards as a sorted string for consistent comparison"""
        card_names = sorted([card['name'] for card in cards])
        return ' | '.join(card_names)
    
    def save_battles(self, player_tag: str, battles: List[Dict]):
        """Save battle log to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for battle in battles:
            # Get player team (should be the only team in the team array)
            teams = battle.get('team', [])
            player_team = None
            
            # Find the player's team
            for team in teams:
                if team.get('tag') == player_tag:
                    player_team = team
                    break
            
            if not player_team:
                continue
            
            # Get opponent data from the 'opponent' field (it's an array)
            opponents = battle.get('opponent', [])
            opponent_team = opponents[0] if opponents else None
            
            # Format deck cards
            deck_cards = self.format_deck(player_team.get('cards', []))
            opponent_deck_cards = self.format_deck(opponent_team.get('cards', [])) if opponent_team else None
            
            # Determine result
            player_crowns = player_team.get('crowns', 0)
            opponent_crowns = opponent_team.get('crowns', 0) if opponent_team else 0
            
            if player_crowns > opponent_crowns:
                result = 'victory'
            elif player_crowns < opponent_crowns:
                result = 'defeat'
            else:
                result = 'draw'
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO battles 
                    (player_tag, battle_time, battle_type, game_mode, is_ladder_tournament,
                     arena_id, arena_name, result, crowns, king_tower_hit_points,
                     princess_towers_hit_points, deck_cards, opponent_tag, opponent_name,
                     opponent_trophies, opponent_deck_cards, trophy_change)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_tag,
                    battle['battleTime'],
                    battle.get('type'),
                    battle.get('gameMode', {}).get('name'),
                    battle.get('isLadderTournament', False),
                    battle.get('arena', {}).get('id'),
                    battle.get('arena', {}).get('name'),
                    result,
                    player_crowns,
                    player_team.get('kingTowerHitPoints'),
                    json.dumps(player_team.get('princessTowersHitPoints', [])),
                    deck_cards,
                    opponent_team.get('tag') if opponent_team else None,
                    opponent_team.get('name') if opponent_team else None,
                    opponent_team.get('startingTrophies') if opponent_team else None,
                    opponent_deck_cards,
                    player_team.get('trophyChange')
                ))
            except sqlite3.Error as e:
                print(f"Error inserting battle: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def update_player_data(self, player_tag: str):
        """Fetch and save latest player data and battles"""
        print(f"Updating data for player {player_tag}...")
        
        # Get player info
        player_info = self.get_player_info(player_tag)
        if player_info:
            self.save_player_info(player_info)
            print(f"Updated player info for {player_info['name']}")
            
            # Update clan data if player is in a clan
            if 'clan' in player_info:
                clan_tag = player_info['clan']['tag']
                print(f"Updating clan data for {player_info['clan']['name']}...")
                clan_info = self.get_clan_info(clan_tag)
                if clan_info:
                    self.save_clan_members(clan_info)
                    print(f"Updated clan data with {len(clan_info.get('memberList', []))} members")
        
        # Get battle log
        battles = self.get_battle_log(player_tag)
        if battles:
            self.save_battles(player_tag, battles)
            print(f"Updated {len(battles)} battles")
        
        # Rate limiting
        time.sleep(1)

def main():
    """Main entry point for GitHub Actions"""
    # Get credentials from environment variables
    API_TOKEN = os.getenv("CR_API_TOKEN")
    PLAYER_TAG = os.getenv("CR_PLAYER_TAG")
    
    if not API_TOKEN:
        print("Error: CR_API_TOKEN environment variable not set")
        exit(1)
    
    if not PLAYER_TAG:
        print("Error: CR_PLAYER_TAG environment variable not set")
        exit(1)
    
    print(f"Starting analysis for player: {PLAYER_TAG}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize analyzer and update data
    analyzer = ClashRoyaleAnalyzer(API_TOKEN)
    analyzer.update_player_data(PLAYER_TAG)
    
    print("Data collection completed successfully!")

if __name__ == "__main__":
    main()