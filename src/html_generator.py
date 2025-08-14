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
            WHERE total_battles >= 3
            ORDER BY win_rate DESC, total_battles DESC
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_card_level_analytics(self) -> Dict:
        """Get card level analytics from enhanced battle data"""
        if not os.path.exists(self.db_path):
            return {}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(battles)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'deck_card_levels' not in columns:
            conn.close()
            return {'message': 'Enhanced battle data not available yet. Will be collected from next battles.'}
        
        analytics = {}
        
        # Average card levels over time
        cursor.execute("""
            SELECT deck_card_levels, opponent_deck_card_levels, player_level, opponent_level, result
            FROM battles 
            WHERE deck_card_levels IS NOT NULL 
            ORDER BY battle_time DESC 
            LIMIT 50
        """)
        
        battles = cursor.fetchall()
        if battles:
            total_player_level = 0
            total_opponent_level = 0
            level_advantage_wins = 0
            level_disadvantage_wins = 0
            total_with_levels = 0
            
            for battle in battles:
                player_level = battle[2]
                opponent_level = battle[3]
                result = battle[4]
                
                if player_level and opponent_level:
                    total_player_level += player_level
                    total_opponent_level += opponent_level
                    total_with_levels += 1
                    
                    if result == 'victory':
                        if player_level > opponent_level:
                            level_advantage_wins += 1
                        elif player_level < opponent_level:
                            level_disadvantage_wins += 1
            
            if total_with_levels > 0:
                analytics['avg_player_level'] = round(total_player_level / total_with_levels, 1)
                analytics['avg_opponent_level'] = round(total_opponent_level / total_with_levels, 1)
                analytics['level_advantage_wins'] = level_advantage_wins
                analytics['level_disadvantage_wins'] = level_disadvantage_wins
                analytics['total_with_levels'] = total_with_levels
        
        # Opponent clan analysis
        cursor.execute("""
            SELECT opponent_clan_name, COUNT(*) as battles, 
                   SUM(CASE WHEN result = 'victory' THEN 1 ELSE 0 END) as wins
            FROM battles 
            WHERE opponent_clan_name IS NOT NULL 
            GROUP BY opponent_clan_name 
            ORDER BY battles DESC 
            LIMIT 10
        """)
        
        clan_battles = cursor.fetchall()
        analytics['opponent_clans'] = [
            {'name': row[0], 'battles': row[1], 'wins': row[2], 'win_rate': round((row[2] / row[1]) * 100, 1)}
            for row in clan_battles
        ]
        
        conn.close()
        return analytics

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
    
    def get_daily_battle_stats(self, days_limit: int = 30) -> List[Dict]:
        """Get daily wins/losses aggregation for histogram, including days with no battles"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, create a complete date range for the last N days
        cursor.execute("""
            WITH RECURSIVE date_range(date) AS (
                SELECT DATE('now', '-' || ? || ' days')
                UNION ALL
                SELECT DATE(date, '+1 day')
                FROM date_range
                WHERE date < DATE('now')
            )
            SELECT 
                dr.date as battle_date,
                COALESCE(SUM(CASE WHEN b.result = 'victory' THEN 1 ELSE 0 END), 0) as wins,
                COALESCE(SUM(CASE WHEN b.result = 'defeat' THEN 1 ELSE 0 END), 0) as losses,
                COALESCE(SUM(CASE WHEN b.result = 'draw' THEN 1 ELSE 0 END), 0) as draws,
                COALESCE(COUNT(b.id), 0) as total_battles
            FROM date_range dr
            LEFT JOIN battles b ON 
                SUBSTR(b.battle_time, 1, 4) || '-' || SUBSTR(b.battle_time, 5, 2) || '-' || SUBSTR(b.battle_time, 7, 2) = dr.date
                AND b.battle_time IS NOT NULL
            GROUP BY dr.date
            ORDER BY dr.date ASC
        """, (days_limit - 1,))  # -1 because we include today
        
        daily_stats = []
        for row in cursor.fetchall():
            daily_stats.append({
                'date': row[0],
                'wins': row[1] or 0,
                'losses': row[2] or 0,
                'draws': row[3] or 0,
                'total_battles': row[4] or 0
            })
        
        conn.close()
        return daily_stats
    
    def get_clan_rankings_data(self, days_limit: int = 7) -> List[Dict]:
        """Get latest clan rankings with progression data"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clan_rankings_history'")
        if not cursor.fetchone():
            conn.close()
            return []
        
        # Get latest rankings
        cursor.execute("""
            SELECT 
                crh.player_tag,
                crh.name,
                crh.clan_rank,
                crh.trophies,
                crh.donations,
                crh.donations_received,
                crh.trophy_change,
                crh.donation_change,
                crh.recorded_at,
                cm.role,
                cm.last_seen
            FROM clan_rankings_history crh
            LEFT JOIN clan_members cm ON crh.player_tag = cm.player_tag
            WHERE crh.recorded_at = (
                SELECT MAX(recorded_at) 
                FROM clan_rankings_history 
                WHERE player_tag = crh.player_tag
            )
            ORDER BY crh.clan_rank ASC
        """)
        
        rankings = []
        for row in cursor.fetchall():
            rankings.append({
                'player_tag': row[0],
                'name': row[1],
                'clan_rank': row[2],
                'trophies': row[3] or 0,
                'donations': row[4] or 0,
                'donations_received': row[5] or 0,
                'trophy_change': row[6] or 0,
                'donation_change': row[7] or 0,
                'recorded_at': row[8],
                'role': row[9] or 'member',
                'last_seen': row[10]
            })
        
        conn.close()
        return rankings
    
    def get_player_clan_progression(self, player_tag: str, days_limit: int = 30) -> List[Dict]:
        """Get specific player's clan ranking progression over time"""
        if not os.path.exists(self.db_path):
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(recorded_at) as date,
                clan_rank,
                trophies,
                trophy_change,
                donations,
                donation_change
            FROM clan_rankings_history 
            WHERE player_tag = ?
                AND DATE(recorded_at) >= DATE('now', '-' || ? || ' days')
            ORDER BY recorded_at DESC
            LIMIT ?
        """, (player_tag, days_limit, days_limit))
        
        progression = []
        for row in cursor.fetchall():
            progression.append({
                'date': row[0],
                'clan_rank': row[1],
                'trophies': row[2] or 0,
                'trophy_change': row[3] or 0,
                'donations': row[4] or 0,
                'donation_change': row[5] or 0
            })
        
        conn.close()
        return progression
    
    def get_clan_deck_analytics(self) -> Dict:
        """Get clan-wide deck and card analytics"""
        if not os.path.exists(self.db_path):
            return {}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clan_member_decks'")
        if not cursor.fetchone():
            conn.close()
            return {}
        
        analytics = {}
        
        # Most popular current decks
        cursor.execute("""
            SELECT deck_cards, COUNT(*) as usage_count, 
                   GROUP_CONCAT(name, ', ') as users
            FROM (
                SELECT DISTINCT player_tag, deck_cards, name
                FROM clan_member_decks cmd1
                WHERE cmd1.id = (
                    SELECT MAX(cmd2.id) 
                    FROM clan_member_decks cmd2 
                    WHERE cmd2.player_tag = cmd1.player_tag
                )
            )
            GROUP BY deck_cards
            ORDER BY usage_count DESC, deck_cards
            LIMIT 10
        """)
        
        popular_decks = []
        for row in cursor.fetchall():
            popular_decks.append({
                'deck_cards': row[0],
                'usage_count': row[1],
                'users': row[2]
            })
        analytics['popular_decks'] = popular_decks
        
        # Most popular favorite cards
        cursor.execute("""
            SELECT favorite_card, COUNT(*) as usage_count,
                   GROUP_CONCAT(name, ', ') as users
            FROM (
                SELECT DISTINCT player_tag, favorite_card, name
                FROM clan_member_decks cmd1
                WHERE favorite_card != ''
                  AND cmd1.id = (
                    SELECT MAX(cmd2.id) 
                    FROM clan_member_decks cmd2 
                    WHERE cmd2.player_tag = cmd1.player_tag
                )
            )
            GROUP BY favorite_card
            ORDER BY usage_count DESC
            LIMIT 10
        """)
        
        favorite_cards = []
        for row in cursor.fetchall():
            favorite_cards.append({
                'card_name': row[0],
                'usage_count': row[1],
                'users': row[2]
            })
        analytics['favorite_cards'] = favorite_cards
        
        # Deck change frequency by player (counting only actual deck composition changes)
        cursor.execute("""
            WITH DeckChanges AS (
                SELECT 
                    player_tag,
                    name,
                    deck_cards,
                    MIN(first_seen) as first_seen,
                    MAX(last_seen) as last_seen,
                    ROW_NUMBER() OVER (PARTITION BY player_tag ORDER BY MIN(first_seen)) as deck_sequence
                FROM clan_member_decks
                GROUP BY player_tag, name, deck_cards
            )
            SELECT 
                player_tag, 
                name, 
                COUNT(*) as deck_changes,
                MIN(first_seen) as first_deck,
                MAX(last_seen) as latest_deck
            FROM DeckChanges
            GROUP BY player_tag, name
            ORDER BY deck_changes DESC
        """)
        
        deck_experimenters = []
        for row in cursor.fetchall():
            deck_experimenters.append({
                'player_tag': row[0],
                'name': row[1],
                'deck_changes': row[2],
                'first_deck': row[3],
                'latest_deck': row[4]
            })
        analytics['deck_experimenters'] = deck_experimenters
        
        conn.close()
        return analytics
    
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
    
    def generate_deck_cards_html(self, deck_cards: str, show_names: bool = True) -> str:
        """Generate HTML for deck cards with images"""
        if not deck_cards:
            return ""
        
        cards = deck_cards.split(' | ')
        cards_html = ""
        
        for card in cards:
            img_path = self.get_card_image_path(card)
            name_html = f'<div class="card-name">{card}</div>' if show_names else ''
            if show_names:
                cards_html += f"""
                <div class="card-container">
                    <img src="{img_path}" alt="{card}" class="card-image" title="{card}" loading="lazy">
                    {name_html}
                </div>
            """
            else:
                cards_html += f'<div class="card-container"><img src="{img_path}" alt="{card}" class="card-image" title="{card}" loading="lazy">{name_html}</div>'
        
        css_class = "deck-cards-compact" if not show_names else "deck-cards"
        return f'<div class="{css_class}">{cards_html}</div>'
    
    def generate_daily_histogram_html(self, daily_stats: List[Dict]) -> str:
        """Generate HTML for daily wins/losses stacked histogram"""
        if not daily_stats:
            return "<p>No daily battle data available for histogram.</p>"
        
        # Find max battles for scaling
        max_battles = max((day['total_battles'] for day in daily_stats), default=1)
        
        # Create custom stacked histogram
        histogram_html = '''
            <div class="chart-container">
                <div class="stacked-histogram">
        '''
        
        for day in daily_stats:
            wins = day['wins']
            losses = day['losses']
            draws = day['draws']
            total = day['total_battles']
            date = day['date']
            
            # Calculate heights as percentages of max battles
            if total == 0:
                win_height = 0
                loss_height = 0
                draw_height = 2  # Minimal height for empty days
            else:
                # Scale based on max battles, with minimum heights for visibility
                scale_factor = (total / max_battles) * 180  # 180px max height
                win_height = max((wins / total) * scale_factor, 1 if wins > 0 else 0)
                loss_height = max((losses / total) * scale_factor, 1 if losses > 0 else 0)
                draw_height = max((draws / total) * scale_factor, 1 if draws > 0 else 0)
            
            # Create tooltip
            tooltip = f"{date}: {wins}W/{losses}L/{draws}D" if total > 0 else f"{date}: No battles"
            
            histogram_html += f'''
                <div class="histogram-bar" title="{tooltip}">
                    <div class="bar-date">{date[-2:]}</div>
                    <div class="bar-stack">
            '''
            
            # Add segments from bottom to top: losses, draws, wins
            if loss_height > 0:
                histogram_html += f'''
                    <div class="bar-segment bar-losses" style="height: {loss_height}px;">
                        {f'<span class="segment-value">{losses}</span>' if losses > 0 else ''}
                    </div>
                '''
            
            if draw_height > 0:
                histogram_html += f'''
                    <div class="bar-segment bar-draws" style="height: {draw_height}px;">
                        {f'<span class="segment-value">{draws}</span>' if draws > 0 else ''}
                    </div>
                '''
            
            if win_height > 0:
                histogram_html += f'''
                    <div class="bar-segment bar-wins" style="height: {win_height}px;">
                        {f'<span class="segment-value">{wins}</span>' if wins > 0 else ''}
                    </div>
                '''
            
            # Handle empty days
            if total == 0:
                histogram_html += f'''
                    <div class="bar-segment bar-empty" style="height: {draw_height}px;">
                    </div>
                '''
            
            histogram_html += '''
                    </div>
                </div>
            '''
        
        histogram_html += '''
                </div>
            </div>
        '''
        
        # Add legend
        legend_html = '''
            <div class="histogram-legend">
                <div class="legend-item">
                    <span class="legend-color legend-wins"></span>
                    <span>Wins</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color legend-losses"></span>
                    <span>Losses</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color legend-draws"></span>
                    <span>Draws</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color legend-empty"></span>
                    <span>No Battles</span>
                </div>
            </div>
        '''
        
        return histogram_html + legend_html
    
    def generate_clan_rankings_html(self, clan_rankings: List[Dict], player_name: str) -> str:
        """Generate HTML for clan rankings with progression indicators"""
        if not clan_rankings:
            return "<p>No clan rankings data available.</p>"
        
        rankings_html = '<div class="clan-rankings">'
        
        for member in clan_rankings:
            is_current_player = member['name'] == player_name
            row_class = "current-player-ranking" if is_current_player else ""
            
            # Trophy change indicator
            trophy_change = member['trophy_change']
            trophy_indicator = ""
            if trophy_change > 0:
                trophy_indicator = f'<span class="trophy-up">+{trophy_change}</span>'
            elif trophy_change < 0:
                trophy_indicator = f'<span class="trophy-down">{trophy_change}</span>'
            else:
                trophy_indicator = '<span class="trophy-neutral">0</span>'
            
            # Donation change indicator
            donation_change = member['donation_change']
            donation_indicator = ""
            if donation_change > 0:
                donation_indicator = f'<span class="donation-up">+{donation_change}</span>'
            elif donation_change < 0:
                donation_indicator = f'<span class="donation-down">{donation_change}</span>'
            else:
                donation_indicator = '<span class="donation-neutral">0</span>'
            
            role_class = {
                'leader': 'leader',
                'coLeader': 'co-leader', 
                'elder': 'elder',
                'member': 'member'
            }.get(member['role'], 'member')
            
            role_display = member['role'].replace('coLeader', 'Co-Leader')
            
            rankings_html += f'''
                <div class="ranking-item {row_class}">
                    <div class="ranking-position">#{member['clan_rank']}</div>
                    <div class="ranking-info">
                        <div class="ranking-header">
                            <span class="member-name">{member['name']}</span>
                            <span class="role-{role_class} member-role">{role_display}</span>
                        </div>
                        <div class="ranking-stats">
                            <div class="stat-group">
                                <span class="trophy-count">🏆 {member['trophies']:,}</span>
                                {trophy_indicator}
                            </div>
                            <div class="stat-group">
                                <span class="donation-count">📦 {member['donations']}↑ {member['donations_received']}↓</span>
                                {donation_indicator}
                            </div>
                            <div class="last-seen-info">
                                🕒 {self.format_time_ago(member['last_seen'])}
                            </div>
                        </div>
                    </div>
                </div>
            '''
        
        rankings_html += '</div>'
        return rankings_html
    
    def generate_clan_deck_analytics_html(self, deck_analytics: Dict) -> str:
        """Generate HTML for clan deck analytics"""
        if not deck_analytics:
            return "<p>No clan deck data available yet. Data will appear after the next hourly collection.</p>"
        
        html = ""
        
        # Popular decks section - REMOVED: Most Popular Clan Decks section
        # popular_decks = deck_analytics.get('popular_decks', [])
        # if popular_decks:
        #     html += '<div class="analytics-section"><h3>🎯 Most Popular Clan Decks</h3>'
        #     for i, deck in enumerate(popular_decks[:5], 1):
        #         deck_cards_html = self.generate_deck_cards_html(deck['deck_cards'], show_names=False)
        #         html += f'''
        #             <div class="popular-deck-item">
        #                 <div class="deck-popularity">
        #                     <span class="deck-rank">#{i}</span>
        #                     <div class="deck-info">
        #                         <span class="usage-count">{deck['usage_count']} member{"s" if deck['usage_count'] > 1 else ""}</span>
        #                         <span class="users-list">{deck['users']}</span>
        #                     </div>
        #                 </div>
        #                 {deck_cards_html}
        #             </div>
        #         '''
        #     html += '</div>'
        
        # Favorite cards section
        favorite_cards = deck_analytics.get('favorite_cards', [])
        if favorite_cards:
            html += '<div class="analytics-section"><h3>⭐ Most Popular Favorite Cards</h3>'
            html += '<div class="favorite-cards-grid">'
            for card in favorite_cards[:8]:
                img_path = self.get_card_image_path(card['card_name'])
                html += f'''
                    <div class="favorite-card-item">
                        <img src="{img_path}" alt="{card['card_name']}" class="favorite-card-image">
                        <div class="favorite-card-info">
                            <span class="card-name">{card['card_name']}</span>
                            <span class="usage-count">{card['usage_count']} member{"s" if card['usage_count'] > 1 else ""}</span>
                        </div>
                    </div>
                '''
            html += '</div></div>'
        
        # Deck experimenters section - REMOVED: Moved to clan member activity table
        # deck_experimenters = deck_analytics.get('deck_experimenters', [])
        # if deck_experimenters:
        #     html += '<div class="analytics-section"><h3>🔄 Deck Experimenters</h3>'
        #     html += '<div class="experimenters-list">'
        #     for member in deck_experimenters[:10]:
        #         changes = member['deck_changes']
        #         if changes > 1:  # Only show people who have changed decks
        #             html += f'''
        #                 <div class="experimenter-item">
        #                     <span class="member-name">{member['name']}</span>
        #                     <span class="change-count">{changes} deck change{"s" if changes > 1 else ""}</span>
        #                 </div>
        #             '''
        #     html += '</div></div>'
        
        return html if html else "<p>No clan deck analytics available yet.</p>"
    
    def generate_card_level_analytics_html(self, analytics: Dict) -> str:
        """Generate HTML for card level and opponent analytics"""
        if not analytics:
            return "<p>Enhanced battle analytics not available yet.</p>"
        
        if 'message' in analytics:
            return f"<p style='color: #666; font-style: italic;'>{analytics['message']}</p>"
        
        html = ""
        
        # Player vs Opponent Level Analysis
        if 'avg_player_level' in analytics:
            html += '<div class="analytics-section">'
            html += '<h3>⚖️ Level Matchmaking Analysis</h3>'
            html += f'''
                <div class="level-comparison">
                    <div class="level-stat">
                        <span class="level-label">Your Avg Level:</span>
                        <span class="level-value">{analytics['avg_player_level']}</span>
                    </div>
                    <div class="level-stat">
                        <span class="level-label">Opponent Avg Level:</span>
                        <span class="level-value">{analytics['avg_opponent_level']}</span>
                    </div>
                </div>
                <div class="level-win-stats">
                    <div class="win-stat">
                        <span class="win-label">Wins with Level Advantage:</span>
                        <span class="win-count">{analytics['level_advantage_wins']}</span>
                    </div>
                    <div class="win-stat">
                        <span class="win-label">Wins with Level Disadvantage:</span>
                        <span class="win-count">{analytics['level_disadvantage_wins']}</span>
                    </div>
                </div>
            '''
            html += '</div>'
        
        # Opponent Clan Analysis
        opponent_clans = analytics.get('opponent_clans', [])
        if opponent_clans:
            html += '<div class="analytics-section">'
            html += '<h3>🏰 Opponent Clan Battles</h3>'
            html += '<div class="opponent-clans-list">'
            
            for clan in opponent_clans[:5]:  # Show top 5
                html += f'''
                    <div class="opponent-clan-item">
                        <div class="clan-name">{clan['name']}</div>
                        <div class="clan-stats">
                            <span class="battles-count">{clan['battles']} battles</span>
                            <span class="win-rate" style="color: {'#38a169' if clan['win_rate'] >= 50 else '#e53e3e'}">{clan['win_rate']}% win rate</span>
                        </div>
                    </div>
                '''
            
            html += '</div></div>'
        
        return html
    
    def generate_clan_favorite_cards_html(self, deck_analytics: Dict) -> str:
        """Generate HTML for just clan favorite cards (for main page)"""
        favorite_cards = deck_analytics.get('favorite_cards', [])
        if not favorite_cards:
            return "<p>No favorite card data available yet. <a href='clan.html' style='color: #4299e1;'>View full clan analytics →</a></p>"
        
        html = '<div class="favorite-cards-grid">'
        for card in favorite_cards[:6]:  # Show only top 6 on main page
            img_path = self.get_card_image_path(card['card_name'])
            html += f'''
                <div class="favorite-card-item">
                    <img src="{img_path}" alt="{card['card_name']}" class="favorite-card-image">
                    <div class="favorite-card-info">
                        <span class="card-name">{card['card_name']}</span>
                        <span class="usage-count">{card['usage_count']} member{"s" if card['usage_count'] > 1 else ""}</span>
                    </div>
                </div>
            '''
        html += '</div>'
        
        # Add link to full clan analytics
        html += '<div style="text-align: center; margin-top: 15px;">'
        html += '<a href="clan.html" style="color: #4299e1; text-decoration: none; font-weight: bold;">View Full Clan Analytics →</a>'
        html += '</div>'
        
        return html
    
    def generate_html_report(self) -> str:
        """Generate complete HTML report for GitHub Pages"""
        stats = self.get_player_stats()
        decks = self.get_deck_performance(10)
        # battles = self.get_recent_battles(15)  # Commented out - Recent Battles section
        daily_stats = self.get_daily_battle_stats(30)
        clan_rankings = self.get_clan_rankings_data()
        # deck_analytics = self.get_clan_deck_analytics()  # Commented out - Clan Favorite Cards section
        # card_level_analytics = self.get_card_level_analytics()  # Commented out - Advanced Battle Analytics section
        
        if not stats:
            return self.generate_error_page()
        
        win_rate = (stats['wins'] / max(stats['total_battles'], 1)) * 100
        
        # Generate deck performance HTML
        deck_performance_html = ""
        for i, deck in enumerate(decks, 1):
            trophy_color = "green" if deck['total_trophy_change'] >= 0 else "red"
            deck_cards_html = self.generate_deck_cards_html(deck['deck_cards'], show_names=False)
            
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
        
        # Generate battle HTML - COMMENTED OUT
        # battles_table_html = ""
        # battles_cards_html = ""
        # 
        # for battle in battles[:10]:
        #     result_class = battle['result']
        #     result_text = battle['result'].upper()
        #     trophy_color = "green" if battle['trophy_change'] >= 0 else "red"
        #     
        #     # Table and card HTML generation
        #     battles_table_html += f"""
        #         <tr class="battle-{result_class}">
        #             <td>{self.format_time_ago(battle['battle_time'])}</td>
        #             <td><span class="result-{result_class}">{result_text}</span></td>
        #             <td>{battle['opponent_name']}</td>
        #             <td>{battle['crowns']}</td>
        #             <td style="color: {trophy_color}">{battle['trophy_change']:+d}</td>
        #             <td>{battle['arena_name']}</td>
        #         </tr>
        #     """
        #     
        #     battles_cards_html += f"""
        #         <div class="battle-card battle-{result_class}">
        #             <div class="battle-card-header">
        #                 <span class="result-{result_class} battle-result">{result_text}</span>
        #                 <span class="battle-time">{self.format_time_ago(battle['battle_time'])}</span>
        #             </div>
        #             <div class="battle-card-content">
        #                 <div class="battle-info">
        #                     <strong>vs {battle['opponent_name']}</strong>
        #                     <span>{battle['arena_name']}</span>
        #                 </div>
        #                 <div class="battle-stats">
        #                     <span class="crown-count">👑 {battle['crowns']}</span>
        #                     <span class="trophy-change" style="color: {trophy_color}">🏆 {battle['trophy_change']:+d}</span>
        #                 </div>
        #             </div>
        #         </div>
        #     """
        
        # Generate daily histogram only (main page)
        daily_histogram_html = self.generate_daily_histogram_html(daily_stats)
        # clan_favorite_cards_html = self.generate_clan_favorite_cards_html(deck_analytics)  # Commented out
        # card_level_analytics_html = self.generate_card_level_analytics_html(card_level_analytics)  # Commented out
        
        return self.generate_full_html(stats, win_rate, deck_performance_html, 
                                     daily_histogram_html)
    
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
    
    def get_base_css_styles(self) -> str:
        """Get base CSS styles used across all pages"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        @font-face {
            font-family: 'Clash-Regular';
            src: url('assets/fonts/Clash_Regular.otf') format('opentype');
            font-weight: normal;
            font-style: normal;
        }
        
        @font-face {
            font-family: 'Supercell-Magic';
            src: url('assets/fonts/Supercell-Magic Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Clash-Regular', 'Supercell-Magic', sans-serif;
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
        
        .deck-cards-compact {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
            justify-content: flex-start;
        }
        
        .deck-cards-compact .card-container {
            flex: 0 0 auto;
            padding: 5px;
            min-width: 50px;
        }
        
        .deck-cards-compact .card-image {
            width: 50px;
            height: 60px;
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
        
        /* Custom Stacked Histogram Styles */
        .chart-container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stacked-histogram {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 200px;
            padding: 20px 10px 30px 10px;
            position: relative;
        }
        
        .histogram-bar {
            flex: 1;
            max-width: 25px;
            margin: 0 2px;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            cursor: pointer;
        }
        
        .bar-date {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8em;
            color: #4a5568;
            font-weight: 500;
        }
        
        .bar-stack {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        
        .bar-segment {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2px;
            position: relative;
            font-size: 0.75em;
            font-weight: bold;
            color: white;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .segment-value {
            opacity: 0.9;
        }
        
        .bar-wins {
            background: linear-gradient(180deg, #48bb78, #38a169);
            border-radius: 2px 2px 0 0;
        }
        
        .bar-losses {
            background: linear-gradient(180deg, #f56565, #e53e3e);
        }
        
        .bar-draws {
            background: linear-gradient(180deg, #ed8936, #dd6b20);
        }
        
        .bar-empty {
            background: linear-gradient(180deg, #cbd5e0, #a0aec0);
            border: 1px dashed #718096;
            border-radius: 2px;
        }
        
        .histogram-legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
            color: #4a5568;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }
        
        .legend-wins {
            background: linear-gradient(180deg, #48bb78, #38a169);
        }
        
        .legend-losses {
            background: linear-gradient(180deg, #f56565, #e53e3e);
        }
        
        .legend-draws {
            background: linear-gradient(180deg, #ed8936, #dd6b20);
        }
        
        .legend-empty {
            background: linear-gradient(180deg, #cbd5e0, #a0aec0);
            border: 1px dashed #718096;
        }
        
        /* Clan Rankings Styles */
        .clan-rankings {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .ranking-item {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }
        
        .ranking-item:hover {
            transform: translateY(-2px);
        }
        
        .current-player-ranking {
            background: rgba(66, 153, 225, 0.15);
            border-left: 4px solid #4299e1;
            font-weight: bold;
        }
        
        .ranking-position {
            font-size: 1.5em;
            font-weight: bold;
            color: #4299e1;
            min-width: 50px;
            text-align: center;
        }
        
        .ranking-info {
            flex: 1;
            margin-left: 20px;
        }
        
        .ranking-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .ranking-stats {
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .stat-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .trophy-up {
            color: #38a169;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .trophy-down {
            color: #e53e3e;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .trophy-neutral {
            color: #718096;
            font-size: 0.9em;
        }
        
        .donation-up {
            color: #3182ce;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .donation-down {
            color: #e53e3e;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .donation-neutral {
            color: #718096;
            font-size: 0.9em;
        }
        
        .last-seen-info {
            color: #718096;
            font-size: 0.9em;
        }
        
        /* Clan Deck Analytics Styles */
        .analytics-section {
            margin-bottom: 30px;
        }
        
        .analytics-section h3 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .popular-deck-item {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .deck-popularity {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .deck-rank {
            font-size: 1.5em;
            font-weight: bold;
            color: #4299e1;
            min-width: 40px;
        }
        
        .deck-info {
            margin-left: 15px;
        }
        
        .usage-count {
            font-weight: bold;
            color: #2d3748;
        }
        
        .users-list {
            color: #718096;
            font-size: 0.9em;
            display: block;
        }
        
        .favorite-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }
        
        .favorite-card-item {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .favorite-card-image {
            width: 50px;
            height: 60px;
            object-fit: contain;
            margin-bottom: 8px;
        }
        
        .favorite-card-info .card-name {
            display: block;
            font-weight: 500;
            color: #2d3748;
            font-size: 0.9em;
        }
        
        .favorite-card-info .usage-count {
            color: #4299e1;
            font-size: 0.8em;
        }
        
        .experimenters-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .experimenter-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 10px 15px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
        }
        
        .experimenter-item .member-name {
            font-weight: 500;
            color: #2d3748;
        }
        
        .experimenter-item .change-count {
            color: #4299e1;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        /* Card Level Analytics Styles */
        .level-comparison {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .level-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .level-label {
            font-weight: 500;
            color: #2d3748;
        }
        
        .level-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #4299e1;
        }
        
        .level-win-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .win-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
        }
        
        .win-label {
            font-size: 0.9em;
            color: #4a5568;
        }
        
        .win-count {
            font-weight: bold;
            color: #38a169;
        }
        
        .opponent-clans-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .opponent-clan-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .clan-name {
            font-weight: 500;
            color: #2d3748;
            font-size: 1.1em;
        }
        
        .clan-stats {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 4px;
        }
        
        .battles-count {
            font-size: 0.9em;
            color: #718096;
        }
        
        .win-rate {
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .clan-analytics-link {
            color: #4299e1;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
            padding: 12px 24px;
            border: 2px solid #4299e1;
            border-radius: 8px;
            display: inline-block;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .clan-analytics-link:hover {
            background: #4299e1;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
        }
        
        @media (max-width: 768px) {
            .deck-cards {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .deck-cards-compact {
                gap: 6px;
            }
            
            .deck-cards-compact .card-container {
                padding: 3px;
                min-width: 40px;
            }
            
            .deck-cards-compact .card-image {
                width: 40px;
                height: 48px;
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
            
            .chart-container {
                padding: 15px;
            }
            
            .stacked-histogram {
                height: 150px;
                padding: 15px 5px 25px 5px;
            }
            
            .histogram-bar {
                max-width: 15px;
                margin: 0 1px;
            }
            
            .bar-date {
                font-size: 0.7em;
                bottom: -20px;
            }
            
            .bar-segment {
                font-size: 0.65em;
            }
            
            .histogram-legend {
                gap: 15px;
            }
            
            .ranking-stats {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }
            
            .ranking-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }
            
            .level-comparison, .level-win-stats {
                grid-template-columns: 1fr;
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
    
    def generate_full_html(self, stats, win_rate, deck_performance_html, 
                          daily_histogram_html) -> str:
        """Generate the complete HTML document"""
        
        css_styles = self.get_base_css_styles()
        
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/charts.css/dist/charts.min.css">
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
            <h2>📊 Daily Battle Activity Log</h2>
            <p style="color: #666; margin-bottom: 15px; font-style: italic;">
                Daily battle history over the last 30 days. Green = wins, red = losses, orange = draws, gray = no battles. Hover for details.
            </p>
            {daily_histogram_html}
        </div>

        <div class="section">
            <h2>🏆 Top Performing Decks</h2>
            {deck_performance_html}
        </div>

        <!-- COMMENTED OUT - Recent Battles Section
        <div class="section">
            <h2>⚔️ Recent Battles</h2>
            <div class="desktop-table">
                <table>
                    <thead><tr><th>Time</th><th>Result</th><th>Opponent</th><th>Crowns</th><th>Trophy Δ</th><th>Arena</th></tr></thead>
                    <tbody>BATTLES_TABLE_HTML</tbody>
                </table>
            </div>
            <div class="battle-cards">BATTLES_CARDS_HTML</div>
        </div>
        -->

        <!-- COMMENTED OUT - Clan Favorite Cards Section
        <div class="section">
            <h2>⭐ Clan Favorite Cards</h2>
            <p style="color: #666; margin-bottom: 15px; font-style: italic;">
                Most popular favorite cards among your clan members.
            </p>
            CLAN_FAVORITE_CARDS_HTML
        </div>
        -->

        <div class="section">
            <h2>🏰 Clan Analytics</h2>
            <p style="color: #666; margin-bottom: 15px; font-style: italic;">
                View detailed clan member statistics, deck analytics, and performance trends.
            </p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="clan.html" class="clan-analytics-link">
                    View Full Clan Analytics →
                </a>
            </div>
        </div>

        <!-- COMMENTED OUT - Advanced Battle Analytics Section
        <div class="section">
            <h2>📈 Advanced Battle Analytics</h2>
            <p style="color: #666; margin-bottom: 15px; font-style: italic;">
                Enhanced analytics including card levels, opponent analysis, and matchmaking fairness.
            </p>
            CARD_LEVEL_ANALYTICS_HTML
        </div>
        -->

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
    
    # Ensure docs directory exists
    os.makedirs('../docs', exist_ok=True)
    
    # Save as index.html for GitHub Pages in docs directory
    with open('../docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("GitHub Pages HTML report generated: ../docs/index.html")

if __name__ == "__main__":
    main()
