import streamlit as st
import pandas as pd
import nfl_data_py as nfl

# Function to fetch data for Chase Claypool's performance
def fetch_claypool_data():
    years = [2022]
    data = []

    for year in years:
        game_log = nfl.import_pbp_data([year])
        #game_log = nfl.game_log
        claypool_data = game_log.dropna(subset=['offense_players'])
        claypool_data = game_log[(claypool_data['play_type'] == 'pass') & (game_log['offense_players'].str.contains('00-0036326'))]
        data.append(claypool_data)

    return pd.concat(data)

claypool_data = fetch_claypool_data()
claypool_data.head()

# Function to create visualizations
def visualize_data(df):
    st.title("Chase Claypool's Performance per Route Run")
    
    # Aggregate metrics
    agg_metrics = df.groupby('game_id').agg(
        routes_run=('play_id', 'count'),
        receiving_yards=('passing_yards', 'sum'),
        targets=('pass_attempt', lambda x: ((x == 1) & (df['receiver_player_id'] == '00-0036326') & (df['play_type'] == 'pass') & (df['sack'] == 0)).sum()),
        touchdowns=('pass_touchdown', lambda x: ((x == 1) & (df['receiver_player_id'] == '00-0036326')).sum()),
        completions=('complete_pass', lambda x: ((x == 1) & (df['receiver_player_id'] == '00-0036326')).sum())
    )
    
    # Calculate final metrics
    agg_metrics['yards_per_route_run'] = agg_metrics['receiving_yards'] / agg_metrics['routes_run']
    agg_metrics['touchdowns_per_route_run'] = agg_metrics['touchdowns'] / agg_metrics['routes_run']
    agg_metrics['completions_per_route_run'] = agg_metrics['completions'] / agg_metrics['routes_run']
    agg_metrics['completion_rate'] = agg_metrics['completions'] / agg_metrics['targets']
    
    # Display aggregate metrics
    st.subheader("Aggregate Metrics for the Season")
    st.write(agg_metrics)
    
def main():
    st.title("Chase Claypool's Performance Analysis")
    claypool_data = fetch_claypool_data()
    visualize_data(claypool_data)

if __name__ == "__main__":
    main()