"""
Find Games Where Both Teams Are Marked HOME
Quick check for games with 'vs.' in both matchups
"""

import pandas as pd
import sys

def find_both_home_games(file_path):
    """
    Find games where both teams are marked as home (both have 'vs.' in MATCHUP).
    
    Args:
        file_path: Path to CSV file to check
    """
    
    print("=" * 80)
    print("FINDING GAMES WHERE BOTH TEAMS ARE MARKED HOME")
    print("=" * 80)
    
    try:
        df = pd.read_csv(file_path)
        print(f"\n✓ Loaded file: {file_path}")
        print(f"  Total rows: {len(df):,}")
        print(f"  Unique games: {df['GAME_ID'].nunique():,}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return
    
    # Identify home vs away
    df['IS_HOME'] = df['MATCHUP'].str.contains('vs.', na=False).astype(int)
    
    print("\n" + "=" * 80)
    print("OVERALL HOME/AWAY DISTRIBUTION")
    print("=" * 80)
    
    home_count = df['IS_HOME'].sum()
    away_count = len(df) - home_count
    
    print(f"\nHome games (vs.): {home_count:,}")
    print(f"Away games (@):   {away_count:,}")
    print(f"Difference:       {abs(home_count - away_count):,}")
    
    # Find games with exactly 2 rows
    game_counts = df['GAME_ID'].value_counts()
    games_with_2 = game_counts[game_counts == 2].index
    
    print(f"\nGames with exactly 2 rows: {len(games_with_2):,}")
    
    # Check each game's home/away composition
    print("\n" + "=" * 80)
    print("CHECKING EACH GAME'S HOME/AWAY STATUS")
    print("=" * 80)
    
    both_home_games = []
    both_away_games = []
    correct_games = []
    
    for game_id in games_with_2:
        game_data = df[df['GAME_ID'] == game_id]
        home_count_game = game_data['IS_HOME'].sum()
        
        if home_count_game == 2:
            both_home_games.append(game_id)
        elif home_count_game == 0:
            both_away_games.append(game_id)
        elif home_count_game == 1:
            correct_games.append(game_id)
    
    print(f"\n✓ Correct games (1 home, 1 away): {len(correct_games):,}")
    print(f"❌ Both teams marked HOME:          {len(both_home_games):,}")
    print(f"❌ Both teams marked AWAY:          {len(both_away_games):,}")
    
    # Show games where both are HOME
    if len(both_home_games) > 0:
        print("\n" + "=" * 80)
        print("GAMES WHERE BOTH TEAMS ARE MARKED HOME")
        print("=" * 80)
        
        print(f"\nFound {len(both_home_games)} games where both teams have 'vs.' in MATCHUP:")
        print("\n" + "-" * 80)
        
        for i, game_id in enumerate(both_home_games, 1):
            game_data = df[df['GAME_ID'] == game_id].sort_values('TEAM_ABBREVIATION')
            
            print(f"\n{i}. GAME_ID: {game_id}")
            print(f"   Date: {game_data['GAME_DATE'].iloc[0]}")
            print(f"   Matchup details:")
            
            for idx, row in game_data.iterrows():
                team = row['TEAM_ABBREVIATION']
                matchup = row['MATCHUP']
                wl = row['WL']
                pts = row.get('PTS', 'N/A')
                
                print(f"      {team:3s} | {matchup:15s} | {wl} | {pts} pts")
            
            # Show what it should be
            teams = game_data['TEAM_ABBREVIATION'].tolist()
            if len(teams) == 2:
                print(f"   → Should be: {teams[0]} vs. {teams[1]}  AND  {teams[1]} @ {teams[0]}")
        
        print("\n" + "-" * 80)
        print("\n💡 TO FIX THESE GAMES:")
        print("   For each game above, one team's MATCHUP should have '@' instead of 'vs.'")
        print("   The away team (visiting team) should have '@', home team has 'vs.'")
        
    else:
        print("\n✅ NO GAMES FOUND WHERE BOTH TEAMS ARE MARKED HOME!")
    
    # Show games where both are AWAY (if any remain)
    if len(both_away_games) > 0:
        print("\n" + "=" * 80)
        print("GAMES WHERE BOTH TEAMS ARE MARKED AWAY")
        print("=" * 80)
        
        print(f"\nFound {len(both_away_games)} games where both teams have '@' in MATCHUP:")
        print("\n" + "-" * 80)
        
        for i, game_id in enumerate(both_away_games, 1):
            game_data = df[df['GAME_ID'] == game_id].sort_values('TEAM_ABBREVIATION')
            
            print(f"\n{i}. GAME_ID: {game_id}")
            print(f"   Date: {game_data['GAME_DATE'].iloc[0]}")
            print(f"   Matchup details:")
            
            for idx, row in game_data.iterrows():
                team = row['TEAM_ABBREVIATION']
                matchup = row['MATCHUP']
                wl = row['WL']
                pts = row.get('PTS', 'N/A')
                
                print(f"      {team:3s} | {matchup:15s} | {wl} | {pts} pts")
            
            # Show what it should be
            teams = game_data['TEAM_ABBREVIATION'].tolist()
            if len(teams) == 2:
                print(f"   → Should be: {teams[0]} vs. {teams[1]}  AND  {teams[1]} @ {teams[0]}")
        
        print("\n" + "-" * 80)
        print("\n💡 TO FIX THESE GAMES:")
        print("   For each game above, one team's MATCHUP should have 'vs.' instead of '@'")
    
    else:
        print("\n✅ NO GAMES FOUND WHERE BOTH TEAMS ARE MARKED AWAY!")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_issues = len(both_home_games) + len(both_away_games)
    
    if total_issues == 0:
        print("\n🎉 PERFECT! All games have correct home/away setup!")
        print(f"   {len(correct_games):,} games ready for processing")
    else:
        print(f"\n⚠️  Total games needing fixes: {total_issues}")
        print(f"   - Both marked HOME: {len(both_home_games)}")
        print(f"   - Both marked AWAY: {len(both_away_games)}")
        print(f"   - Correct games: {len(correct_games):,}")
        
        print("\n📝 Next steps:")
        print("   1. Fix the games listed above in your source data")
        print("   2. Re-run this script to verify all fixed")
        print("   3. Then proceed with 03_create_game_level.py")
    
    print("\n" + "=" * 80)
    
    # Optionally save problematic games to CSV for easier fixing
    if total_issues > 0:
        problem_game_ids = both_home_games + both_away_games
        problem_rows = df[df['GAME_ID'].isin(problem_game_ids)].sort_values(['GAME_ID', 'TEAM_ABBREVIATION'])
        
        output_file = file_path.replace('.csv', '_PROBLEMS.csv')
        problem_rows.to_csv(output_file, index=False)
        print(f"\n💾 Saved problematic games to: {output_file}")
        print(f"   You can open this in Excel to fix them more easily")


if __name__ == "__main__":
    
    # Default file path
    FILE_PATH = "data/processed/nba/nba_team_game_data.csv"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        FILE_PATH = sys.argv[1]
    
    print(f"\nFile to check: {FILE_PATH}\n")
    
    find_both_home_games(FILE_PATH)
    
    print("\n✅ Check complete!")