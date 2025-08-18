import os, argparse, json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from datetime import datetime

def crosscn_asn_processor(raw_data, asn_list,
                          pri_cspec='tab20', sup_cspec='viridis', num_sup=10):

    pri_cmap = plt.get_cmap(pri_cspec)
    sup_cmap = plt.get_cmap(sup_cspec).resampled(num_sup + 1) # add one for 'other'
    keys = list(raw_data.keys())
    dt_keys = [datetime.strptime(key, '%y-%m-%d') for key in keys]
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
    ax1, ax2 = axes[0], axes[1]
    
    # graph 1: bar chart on total probe
    ax1.bar(dt_keys, [raw_data[key].get('counter', 0) for key in keys])
    ax1.set_ylabel('total completed probes')

    # graph 2: bar chart on ASN composition
    bottom = [0] * len(keys)
    for i, asn in enumerate(asn_list):
        ratios = [raw_data[key]['asn-dist'].get(asn, 0) for key in keys if raw_data[key].get('counter', 0) != 0]
        ax2.bar(dt_keys, ratios, bottom=bottom, label=asn, color=pri_cmap(i) if i < 20 else sup_cmap(i - 20))
        bottom = [b + v for b, v, in zip(bottom, ratios)] 
    ax2.bar(dt_keys, [1.0 - b for b in bottom], bottom=bottom, label='other', color=sup_cmap(num_sup))
    ax2.legend(title='asn', loc='center left', bbox_to_anchor=(1.01, 0.5), borderaxespad=0, frameon=False) 
    ax2.set_ylabel('ASN proportion in inter-country path')
    ax2.set_xlabel('date')

    plt.tight_layout()
    plt.close(fig)
    return fig

