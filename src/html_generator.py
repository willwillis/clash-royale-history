#!/usr/bin/env python3
"""
HTML Report Generator for GitHub Pages
Generates Clash Royale analytics with relative paths for GitHub Pages
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

class GitHubPagesHTMLGenerator:
    def __init__(self, db_path: str = "clash_royale.db"):
        self.db_path = db_path
        
        # Card name mapping for file names (GitHub Pages uses relative paths)
        self.card_name_mapping = {
            'Three Musketeers': '3M',
            'Archer Queen': 'ArcherQueen',
            'Baby Dragon': 'BabyD',
            'Barbarian Barrel': 'BarbBarrel',
            'Barbarians': 'Barbs',
            'Goblin Barrel': 'Barrel',
            'Bomb Tower': 'BombTower',
            'Boss Bandit': 'BossBandit',
            'Cannon Cart': 'CannonCart',
            'Dark Prince': 'DarkPrince',
            'Dart Goblin': 'DartGob',
            'Electro Giant': 'ElectroGiant',
            'Electro Spirit': 'ElectroSpirit',
            'Elixir Golem': 'ElixirGolem',
            'Executioner': 'Exe',
            'Fire Spirit': 'FireSpirit',
            'Flying Machine': 'FlyingMachine',
            'Goblin Gang': 'GobGang',
            'Goblin Giant': 'GobGiant',
            'Goblin Hut': 'GobHut',
            'Goblin Cage': 'GoblinCage',
            'Goblin Curse': 'GoblinCurse',
            'Goblin Demolisher': 'GoblinDemolisher',
            'Goblin Drill': 'GoblinDrill',
            'Goblin Machine': 'GoblinMachine',
            'Spear Goblins': 'Gobs',
            'Golden Knight': 'GoldenKnight',
            'Giant Skeleton': 'GiantSkelly',
            'Heal Spirit': 'HealSpirit',
            'Hog Rider': 'Hog',
            'Minion Horde': 'Horde',
            'Ice Golem': 'IceGolem',
            'Ice Spirit': 'IceSpirit',
            'Ice Wizard': 'IceWiz',
            'Inferno Tower': 'Inferno',
            'Inferno Dragon': 'InfernoD',
            'Lava Hound': 'Lava',
            'Little Prince': 'LittlePrince',
            'The Log': 'Log',
            'Lumberjack': 'Lumber',
            'Mega Minion': 'MM',
            'Mini P.E.K.K.A': 'MP',
            'Magic Archer': 'MagicArcher',
            'Mega Knight': 'MegaKnight',
            'Mighty Miner': 'MightyMiner',
            'Mother Witch': 'MotherWitch',
            'Musketeer': 'Musk',
            'Night Witch': 'NightWitch',
            'P.E.K.K.A': 'PEKKA',
            'Elixir Collector': 'Pump',
            'Royal Giant': 'RG',
            'Battle Ram': 'Ram',
            'Ram Rider': 'RamRider',
            'Royal Delivery': 'RoyalDelivery',
            'Royal Hogs': 'RoyalHogs',
            'Royal Recruits': 'RoyalRecruits',
            'Skeleton Army': 'Skarmy',
            'Skeleton Dragons': 'SkeletonDragons',
            'Skeleton King': 'SkeletonKing',
            'Skeletons': 'Skellies',
            'Skeleton Barrel': 'SkellyBarrel',
            'Giant Snowball': 'Snowball',
            'Spear Goblins': 'SpearGobs',
            'Spirit Empress': 'SpiritEmpress',
            'Suspicious Bush': 'SuspiciousBush',
            'Valkyrie': 'Valk',
            'Wall Breakers': 'WallBreakers',
            'Wizard': 'Wiz',
            'X-Bow': 'XBow',
            'Elite Barbarians': 'eBarbs',
            'Electro Dragon': 'eDragon',
            'Electro Wizard': 'eWiz'
        }
    
    def get_card_filename(self, card_name: str) -> str:
        """Convert card name to filename"""
        return self.card_name_mapping.get(card_name, card_name.replace(' ', '').replace('.', '').replace('-', ''))
    
    def get_card_image_path(self, card_name: str) -> str:
        """Get the relative path to card image for GitHub Pages"""
        filename = self.get_card_filename(card_name)
        
        # Try normal cards first
        normal_path = f"cards/normal_cards/{filename}.png"
        evolution_path = f"cards/evolution_cards/{filename}.png"
        
        # Check if files exist (look in parent directory when running from src/)
        cards_base = "../cards" if os.path.exists("../cards") else "cards"
        
        if os.path.exists(f"{cards_base}/normal_cards/{filename}.png"):
            return normal_path
        elif os.path.exists(f"{cards_base}/evolution_cards/{filename}.png"):
            return evolution_path
        else:
            # Fallback to placeholder
            return f"https://via.placeholder.com/100x120/7B68EE/FFFFFF?text={card_name.replace(' ', '+')}"
    
    def get_player_stats(self) -> Optional[Dict]:
        """Get player statistics from database"""
        if not os.path.exists(self.db_path):
            return None
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get player info
        cursor.execute("SELECT * FROM players ORDER BY last_updated DESC LIMIT 1")
        player_row = cursor.fetchone()
        
        if not player_row:
            conn.close()
            return None
            
        # Get battle stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_battles,
                SUM(CASE WHEN result = 'victory' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'defeat' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) as draws,
                SUM(COALESCE(trophy_change, 0)) as total_trophy_change,
                MAX(battle_time) as last_battle,
                MIN(battle_time) as first_battle
            FROM battles
        """)
        battle_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'player_tag': player_row[0],
            'name': player_row[1],
            'trophies': player_row[2],
            'best_trophies': player_row[3],
            'level': player_row[4],
            'clan_tag': player_row[5],
            'clan_name': player_row[6],
            'last_updated': player_row[7],
            'total_battles': battle_stats[0] or 0,
            'wins': battle_stats[1] or 0,
            'losses': battle_stats[2] or 0,
            'draws': battle_stats[3] or 0,
            'total_trophy_change': battle_stats[4] or 0,
            'last_battle': battle_stats[5],
            'first_battle': battle_stats[6]
        }
    
    def get_deck_performance(self, limit: int = 10) -> List[Dict]:
        """Get deck performance data"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM deck_performance 
            WHERE total_battles >= 1
            ORDER BY win_rate DESC, total_battles DESC
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_recent_battles(self, limit: int = 15) -> List[Dict]:
        """Get recent battle data"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT battle_time, result, opponent_name, opponent_tag, 
                   crowns, trophy_change, deck_cards, arena_name
            FROM battles 
            ORDER BY battle_time DESC 
            LIMIT ?
        """, (limit,))
        
        battles = []
        for row in cursor.fetchall():
            battles.append({
                'battle_time': row[0],
                'result': row[1],
                'opponent_name': row[2] or 'Unknown',
                'opponent_tag': row[3] or '',
                'crowns': row[4] or 0,
                'trophy_change': row[5] or 0,
                'deck_cards': row[6] or '',
                'arena_name': row[7] or 'Unknown'
            })
        
        conn.close()
        return battles
    
    def get_clan_members(self) -> List[Dict]:
        """Get clan member data"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, role, trophies, donations, donations_received, last_seen
            FROM clan_members 
            ORDER BY 
                CASE role 
                    WHEN 'leader' THEN 1 
                    WHEN 'coLeader' THEN 2 
                    WHEN 'elder' THEN 3 
                    ELSE 4 
                END,
                trophies DESC
        """)
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'name': row[0],
                'role': row[1],
                'trophies': row[2] or 0,
                'donations': row[3] or 0,
                'donations_received': row[4] or 0,
                'last_seen': row[5]
            })
        
        conn.close()
        return members
    
    def format_time_ago(self, timestamp: str) -> str:
        """Format timestamp as time ago"""
        if not timestamp or timestamp == 'never':
            return "never"
            
        try:
            if 'T' in timestamp:
                if timestamp.endswith('Z'):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(timestamp)
            else:
                dt = datetime.fromisoformat(timestamp)
                
            now = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
                
            time_diff = now - dt
            
            if time_diff.days > 0:
                return f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"{hours} hours ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "just now"
        except:
            return "unknown"
    
    def format_date(self, timestamp: str) -> str:
        """Format timestamp as readable date"""
        if not timestamp:
            return "unknown"
            
        try:
            if 'T' in timestamp:
                if timestamp.endswith('Z'):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(timestamp)
            else:
                dt = datetime.fromisoformat(timestamp)
                
            return dt.strftime('%B %d, %Y')
        except:
            return "unknown"
    
    def generate_deck_cards_html(self, deck_cards: str) -> str:
        """Generate HTML for deck cards with images"""
        if not deck_cards:
            return ""
        
        cards = deck_cards.split(' | ')
        cards_html = ""
        
        for card in cards:
            img_path = self.get_card_image_path(card)
            cards_html += f"""
                <div class="card-container">
                    <img src="{img_path}" alt="{card}" class="card-image" title="{card}" loading="lazy">
                    <div class="card-name">{card}</div>
                </div>
            """
        
        return f'<div class="deck-cards">{cards_html}</div>'
    
    def generate_html_report(self) -> str:
        """Generate complete HTML report for GitHub Pages"""
        stats = self.get_player_stats()
        decks = self.get_deck_performance(10)
        battles = self.get_recent_battles(15)
        clan_members = self.get_clan_members()
        
        if not stats:
            return self.generate_error_page()
        
        win_rate = (stats['wins'] / max(stats['total_battles'], 1)) * 100
        
        # Generate deck performance HTML
        deck_performance_html = ""
        for i, deck in enumerate(decks, 1):
            trophy_color = "green" if deck['total_trophy_change'] >= 0 else "red"
            deck_cards_html = self.generate_deck_cards_html(deck['deck_cards'])
            
            deck_performance_html += f"""
                <div class="deck-item">
                    <div class="deck-header">
                        <h3>#{i} - {deck['win_rate']}% Win Rate</h3>
                        <div class="deck-stats">
                            <span class="stat">🏆 {deck['total_battles']} battles</span>
                            <span class="stat">✅ {deck['wins']} wins</span>
                            <span class="stat">❌ {deck['losses']} losses</span>
                            <span class="stat" style="color: {trophy_color}">📈 {deck['total_trophy_change']:+d} trophies</span>
                            <span class="stat">👑 {deck['avg_crowns']:.1f} avg crowns</span>
                        </div>
                    </div>
                    {deck_cards_html}
                </div>
            """
        
        # Generate battle and clan HTML using the same responsive approach as before
        # (Shortened for brevity - would include the same mobile-responsive tables/cards)
        
        battles_table_html = ""
        battles_cards_html = ""
        
        for battle in battles[:10]:
            result_class = battle['result']
            result_text = battle['result'].upper()
            trophy_color = "green" if battle['trophy_change'] >= 0 else "red"
            
            # Table and card HTML generation (same as previous version)
            battles_table_html += f"""
                <tr class="battle-{result_class}">
                    <td>{self.format_time_ago(battle['battle_time'])}</td>
                    <td><span class="result-{result_class}">{result_text}</span></td>
                    <td>{battle['opponent_name']}</td>
                    <td>{battle['crowns']}</td>
                    <td style="color: {trophy_color}">{battle['trophy_change']:+d}</td>
                    <td>{battle['arena_name']}</td>
                </tr>
            """
            
            battles_cards_html += f"""
                <div class="battle-card battle-{result_class}">
                    <div class="battle-card-header">
                        <span class="result-{result_class} battle-result">{result_text}</span>
                        <span class="battle-time">{self.format_time_ago(battle['battle_time'])}</span>
                    </div>
                    <div class="battle-card-content">
                        <div class="battle-info">
                            <strong>vs {battle['opponent_name']}</strong>
                            <span>{battle['arena_name']}</span>
                        </div>
                        <div class="battle-stats">
                            <span class="crown-count">👑 {battle['crowns']}</span>
                            <span class="trophy-change" style="color: {trophy_color}">🏆 {battle['trophy_change']:+d}</span>
                        </div>
                    </div>
                </div>
            """
        
        # Generate clan HTML (same responsive pattern)
        clan_table_html = ""
        clan_cards_html = ""
        
        for member in clan_members[:20]:
            is_current_player = member['name'] == stats['name']  # Use actual player name from stats
            row_class = "current-player" if is_current_player else ""
            card_class = "current-player-card" if is_current_player else ""
            
            role_class = {
                'leader': 'leader',
                'coLeader': 'co-leader', 
                'elder': 'elder',
                'member': 'member'
            }.get(member['role'], 'member')
            
            role_display = member['role'].replace('coLeader', 'Co-Leader')
            
            clan_table_html += f"""
                <tr class="{row_class}">
                    <td>{member['name']}</td>
                    <td><span class="role-{role_class}">{role_display}</span></td>
                    <td>{member['trophies']:,}</td>
                    <td>{member['donations']}↑ {member['donations_received']}↓</td>
                    <td>{self.format_time_ago(member['last_seen'])}</td>
                </tr>
            """
            
            clan_cards_html += f"""
                <div class="clan-member-card {card_class}">
                    <div class="member-card-header">
                        <strong class="member-name">{member['name']}</strong>
                        <span class="role-{role_class} member-role">{role_display}</span>
                    </div>
                    <div class="member-card-content">
                        <div class="member-stats">
                            <span class="trophy-count">🏆 {member['trophies']:,}</span>
                            <span class="donation-stats">📦 {member['donations']}↑ {member['donations_received']}↓</span>
                        </div>
                        <div class="member-activity">
                            <span class="last-seen">🕒 {self.format_time_ago(member['last_seen'])}</span>
                        </div>
                    </div>
                </div>
            """
        
        return self.generate_full_html(stats, win_rate, deck_performance_html, 
                                     battles_table_html, battles_cards_html,
                                     clan_table_html, clan_cards_html)
    
    def generate_error_page(self) -> str:
        """Generate error page when no data is available"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clash Royale Analytics - No Data</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .error-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>⚔️ Clash Royale Analytics</h1>
        <h2>No Data Available</h2>
        <p>The analytics data is being generated. Please check back in a few minutes.</p>
        <p>Data is automatically updated every hour via GitHub Actions.</p>
    </div>
</body>
</html>
        """
    
    def generate_full_html(self, stats, win_rate, deck_performance_html, 
                          battles_table_html, battles_cards_html,
                          clan_table_html, clan_cards_html) -> str:
        """Generate the complete HTML document"""
        
        # Complete CSS styles for GitHub Pages
        css_styles = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .header h1 {
            color: #4a5568;
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        
        .player-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card h3 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #4299e1;
        }
        
        .section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .section h2 {
            color: #2d3748;
            margin-bottom: 25px;
            border-bottom: 3px solid #4299e1;
            padding-bottom: 10px;
        }
        
        .deck-item {
            background: rgba(247, 250, 252, 0.8);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }
        
        .deck-header {
            margin-bottom: 15px;
        }
        
        .deck-header h3 {
            color: #2d3748;
            margin-bottom: 8px;
        }
        
        .deck-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .stat {
            background: rgba(255, 255, 255, 0.8);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .deck-cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        
        .card-container {
            text-align: center;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .card-image {
            width: 60px;
            height: 72px;
            object-fit: contain;
            border-radius: 5px;
        }
        
        .card-name {
            font-size: 0.8em;
            margin-top: 5px;
            color: #4a5568;
            font-weight: 500;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            overflow: hidden;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        
        th {
            background: #4299e1;
            color: white;
            font-weight: 600;
        }
        
        .battle-victory {
            background-color: rgba(72, 187, 120, 0.1);
        }
        
        .battle-defeat {
            background-color: rgba(245, 101, 101, 0.1);
        }
        
        .battle-draw {
            background-color: rgba(237, 137, 54, 0.1);
        }
        
        .result-victory {
            color: #38a169;
            font-weight: bold;
        }
        
        .result-defeat {
            color: #e53e3e;
            font-weight: bold;
        }
        
        .result-draw {
            color: #ed8936;
            font-weight: bold;
        }
        
        .current-player {
            background-color: rgba(66, 153, 225, 0.2);
            font-weight: bold;
        }
        
        .role-leader {
            color: #d69e2e;
            font-weight: bold;
        }
        
        .role-co-leader {
            color: #3182ce;
            font-weight: bold;
        }
        
        .role-elder {
            color: #38a169;
            font-weight: bold;
        }
        
        .role-member {
            color: #718096;
        }
        
        /* Mobile Battle Cards */
        .battle-cards {
            display: none;
        }
        
        .battle-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #e2e8f0;
        }
        
        .battle-card.battle-victory {
            border-left-color: #38a169;
            background-color: rgba(72, 187, 120, 0.05);
        }
        
        .battle-card.battle-defeat {
            border-left-color: #e53e3e;
            background-color: rgba(245, 101, 101, 0.05);
        }
        
        .battle-card.battle-draw {
            border-left-color: #ed8936;
            background-color: rgba(237, 137, 54, 0.05);
        }
        
        .battle-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .battle-result {
            font-size: 1.1em;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.8);
        }
        
        .battle-time {
            color: #718096;
            font-size: 0.9em;
        }
        
        .battle-card-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .battle-info {
            display: flex;
            flex-direction: column;
        }
        
        .battle-info span {
            color: #718096;
            font-size: 0.9em;
        }
        
        .battle-stats {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 5px;
        }
        
        .crown-count, .trophy-change {
            padding: 3px 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }
        
        /* Mobile Clan Member Cards */
        .clan-member-cards {
            display: none;
        }
        
        .clan-member-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #e2e8f0;
        }
        
        .current-player-card {
            border-left-color: #4299e1;
            background: rgba(66, 153, 225, 0.1);
        }
        
        .member-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .member-name {
            font-size: 1.1em;
            color: #2d3748;
        }
        
        .member-role {
            padding: 3px 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .member-card-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .member-stats {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .trophy-count, .donation-stats {
            padding: 3px 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }
        
        .member-activity {
            text-align: right;
        }
        
        .last-seen {
            color: #718096;
            font-size: 0.9em;
            padding: 3px 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.8);
        }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 30px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .deck-cards {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .player-stats {
                grid-template-columns: 1fr;
            }
            
            .deck-stats {
                flex-direction: column;
            }
            
            /* Hide tables on mobile, show cards */
            .desktop-table {
                display: none;
            }
            
            .battle-cards {
                display: block;
            }
            
            .clan-member-cards {
                display: block;
            }
            
            .container {
                padding: 10px;
            }
            
            .section {
                padding: 20px;
            }
            
            .header {
                padding: 20px;
            }
        }
        
        @media (min-width: 769px) {
            .desktop-table {
                display: block;
            }
            
            .battle-cards {
                display: none;
            }
            
            .clan-member-cards {
                display: none;
            }
        }
        """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clash Royale Analytics - {stats['name']}</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <style>{css_styles}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ Clash Royale Battle Analytics</h1>
            <div class="player-info">
                <h2>{stats['name']} ({stats['player_tag']})</h2>
                <p>Clan: {stats['clan_name'] or 'None'} | Level: {stats['level']}</p>
                <p style="font-style: italic; color: #666; margin-top: 10px;">
                    <strong>Player statistics since {self.format_date(stats['first_battle'])}</strong><br>
                    Statistics are calculated from battles collected since data tracking began and do not reflect lifetime totals.
                </p>
            </div>
            <div class="player-stats">
                <div class="stat-card">
                    <h3>Current Trophies</h3>
                    <div class="value">{stats['trophies']:,}</div>
                    <small>Best: {stats['best_trophies']:,}</small>
                </div>
                <div class="stat-card">
                    <h3>Win Rate</h3>
                    <div class="value">{win_rate:.1f}%</div>
                    <small>{stats['wins']}W / {stats['losses']}L</small>
                </div>
                <div class="stat-card">
                    <h3>Total Battles</h3>
                    <div class="value">{stats['total_battles']}</div>
                    <small>{stats['draws']} draws</small>
                </div>
                <div class="stat-card">
                    <h3>Trophy Change</h3>
                    <div class="value" style="color: {'green' if stats['total_trophy_change'] >= 0 else 'red'}">{stats['total_trophy_change']:+d}</div>
                    <small>Total from battles</small>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🏆 Top Performing Decks</h2>
            {deck_performance_html}
        </div>

        <div class="section">
            <h2>⚔️ Recent Battles</h2>
            <div class="desktop-table">
                <table>
                    <thead><tr><th>Time</th><th>Result</th><th>Opponent</th><th>Crowns</th><th>Trophy Δ</th><th>Arena</th></tr></thead>
                    <tbody>{battles_table_html}</tbody>
                </table>
            </div>
            <div class="battle-cards">{battles_cards_html}</div>
        </div>

        <div class="section">
            <h2>🏰 Clan Member Activity</h2>
            <div class="desktop-table">
                <table>
                    <thead><tr><th>Name</th><th>Role</th><th>Trophies</th><th>Donations</th><th>Last Seen</th></tr></thead>
                    <tbody>{clan_table_html}</tbody>
                </table>
            </div>
            <div class="clan-member-cards">{clan_cards_html}</div>
        </div>

        <div class="footer">
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Data last updated: {self.format_time_ago(stats['last_updated'])}</p>
            <p>Automatically updated via GitHub Actions</p>
        </div>
    </div>
</body>
</html>
        """

def main():
    """Generate HTML report for GitHub Pages"""
    generator = GitHubPagesHTMLGenerator()
    html_content = generator.generate_html_report()
    
    # Save as index.html for GitHub Pages
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("GitHub Pages HTML report generated: index.html")

if __name__ == "__main__":
    main()