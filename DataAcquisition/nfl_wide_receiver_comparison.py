#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import nfl_data_py as nfl

# Fetch raw data 
def fetch_player_data():
    data = []

    for year in years:
        game_log = nfl.import_pbp_data([year])
        player_data = game_log.dropna(subset=['offense_players'])
        player_data = player_data[(player_data['play_type'] == 'pass') &
                                  #(player_data['game_id'] == '2020_10_CIN_PIT') &
                                  #(player_data['receiver_player_id'] == '00-0036326') &
                                  #(player_data['desc'].str.contains('Claypool')) &
                                  #(player_data['penalty'] == 1) &
                                  #(player_data['pass_attempt'] == 1) &
                                  (player_data['play_deleted'] == 0) &
                                  (player_data['offense_players'].str.contains('00-0036326'))
                                 ]
        data.append(player_data)

    return pd.concat(data)

#player_data = fetch_player_data()
#player_data

# Function to create visualizations
def visualize_data(df):
    st.title("Player's Performance per Route Run")
    
    # Aggregate metrics
    agg_metrics = df.groupby('game_id').agg(
            routes_run=('play_id', 'count'),
            # For receiving_yards, we need to consider laterals
            receiving_yards=('passing_yards', lambda x: x[((player_data.loc[x.index, 'receiver_player_id'] == '00-0036326') | 
                                                           (player_data.loc[x.index, 'lateral_receiver_player_id'] == '00-0036326')) & 
                                                          (player_data.loc[x.index, 'sack'] == 0) ].sum()),
            targets=('pass_attempt', lambda x: ((x == 1) & (player_data['receiver_player_id'] == '00-0036326') & 
                                                           (player_data['play_type'] == 'pass') & 
                                                           (player_data['sack'] == 0)).sum()),
            touchdowns=('pass_touchdown', lambda x: ((x == 1) & (player_data['receiver_player_id'] == '00-0036326')).sum()),
            completions=('complete_pass', lambda x: ((x == 1) & (player_data['receiver_player_id'] == '00-0036326')).sum())
        )

    # Calculate final metrics
    agg_metrics['yards_per_route_run'] = agg_metrics['receiving_yards'] / agg_metrics['routes_run']
    agg_metrics['touchdowns_per_route_run'] = agg_metrics['touchdowns'] / agg_metrics['routes_run']
    agg_metrics['targets_per_route_run'] = agg_metrics['targets'] / agg_metrics['routes_run']
    agg_metrics['completions_per_route_run'] = agg_metrics['completions'] / agg_metrics['routes_run']
    agg_metrics['completion_rate'] = agg_metrics['completions'] / agg_metrics['targets']
    
    # Display aggregate metrics
    st.subheader("Aggregate Metrics for the Season")
    st.write(agg_metrics)

def main():
    st.title("NFL Player's Performance Analysis")
    
    # User input for year range
    start_year, end_year = st.slider(
        "Select Year Range",
        min_value=2000,
        max_value=2024,
        value=(2022, 2023)
    )
    
    years = list(range(start_year, end_year + 1))
    
    st.write(f"Fetching data for years: {years}")
    
    player_data = fetch_player_data(years)
    visualize_data(player_data)

if __name__ == "__main__":
    main()


# In[ ]:




