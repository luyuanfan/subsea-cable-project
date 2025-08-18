import matplotlib.pyplot as plt
import gzip, argparse, json, statistics, re
from datetime import datetime

def prelim_image_processor(data, rtt_threshold=None, hop_threshold=None):
    rtt_dts, hop_dts, rtts, hopnums = [], [], [], []
    for inst in data:
        if not hop_threshold or inst['hop-num'] <= hop_threshold:
            hop_dts.append(datetime.strptime(inst['datetime'], '%Y-%m-%d %H:%M:%S.%f%z'))
            hopnums.append(inst['hop-num'])
        rtt_stats = statistics.mean(inst['last-rtts'])
        if not rtt_threshold or rtt_stats <= rtt_threshold:
            rtt_dts.append(datetime.strptime(inst['datetime'], '%Y-%m-%d %H:%M:%S.%f%z'))
            rtts.append(statistics.mean(inst['last-rtts']))
    
    fig1, ax1 = plt.subplots(figsize=(15, 10))
    ax1.scatter(rtt_dts, rtts, alpha=0.4)
    ax1.set_xlabel('probe time')
    ax1.set_ylabel('round-trip time')
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(15, 10))
    ax2.set_xlabel('probe time')
    ax2.set_ylabel('hop number')
    ax2.scatter(hop_dts, hopnums, alpha=0.4)
    plt.close(fig2)

    return fig1, fig2
