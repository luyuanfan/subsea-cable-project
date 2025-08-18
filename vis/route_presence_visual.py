import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse, json
from .utils.date_processing import generate_date_sequence

def format_ip(ip_addr : str) -> tuple[int]:
    ip_addr = '.'.join(ip_addr.split('->'))
    return tuple(map(int, ip_addr.split('.')))
 
def heatmap_image_processor(data, start_time, end_time, 
                    threshold=40, mode='both', contiguous_flag=False):
    
    dates = data.keys()
    dates = list(sorted(dates))
    formatted_data = []
    for day in dates:
        for inst in data[day]:
            formatted_data.append({'date': day, 'node': inst['node'], 'count': inst['count']})

    df = pd.DataFrame(formatted_data)
    sorted_df = df.sort_values(by='count', ascending=False)
    top_ip_rows = sorted_df.drop_duplicates(subset='node').head(threshold)
    filtered_ips = top_ip_rows['node'].unique()
    filtered_ips_set = set(filtered_ips)
    filtered_df = df[df['node'].isin(filtered_ips_set)]    
    filtered_pivot_df = filtered_df.pivot_table(index='node', columns='date', values='count', observed=False).fillna(0)
    if contiguous_flag:
        contiguous_dates = generate_date_sequence(start_time, end_time)
        filtered_pivot_df = filtered_pivot_df.reindex(columns=contiguous_dates, fill_value=0)
    fig1, fig2 = None, None
    if mode == 'presence' or mode == 'both':
        presence_df = (filtered_pivot_df > 0).astype(int)
        fig1, ax1 = plt.subplots(figsize=(20, 15))
        sns.heatmap(presence_df, cmap='Blues', cbar=False, linewidth=0.5,
        linecolor='lightgray', ax=ax1)    
        ax1.set_yticks(np.arange(len(presence_df.index)) + 0.5) 
        ax1.set_yticklabels(presence_df.index.tolist(), rotation=0, fontsize=10)
        ax1.tick_params(axis='x', rotation=90)
        plt.close(fig1)
    if mode == 'density' or mode == 'both':
        fig2, ax2 = plt.subplots(figsize=(20, 15))
        sns.heatmap(filtered_pivot_df, cmap='Blues', cbar=True, linewidth=0.5,
        linecolor='lightgray', ax=ax2)    
        ax2.set_yticks(np.arange(len(filtered_pivot_df.index)) + 0.5)
        ax2.set_yticklabels(filtered_pivot_df.index.tolist(), rotation=0, fontsize=10)
        ax2.tick_params(axis='x', rotation=90)
        plt.close(fig2)
    return (fig1, fig2) if fig1 else (fig2, fig1)
