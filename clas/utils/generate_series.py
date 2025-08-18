import json, statistics
import numpy as np
from datetime import datetime

def parse_hopdata(raw_data, subject, aggre, spec):

    raw_data = sorted(raw_data, key=lambda x : datetime.fromisoformat(x['datetime']))
    dts, stats_data = [], []
    dates = set()

    if not aggre:
        for item in raw_data:
            dt = datetime.fromisoformat(item['datetime']).replace(tzinfo=None)
            dts.append(dt)
            dates.add(dt.date())
            stats_data.append(item['hop-num'] if subject == 'hop number' else statistics.mean(item['last-rtts']))

        return list(dates), dts, stats_data
    
    buf = []
    for i, item in enumerate(raw_data):
        dt = datetime.fromisoformat(item['datetime']).replace(tzinfo=None)
        dt = dt.date()
        dates.add(dt)
        if len(dts) == 0:
            dts.append(dt)
            buf.append(item['hop-num'] if subject == 'hop number' else statistics.mean(item['last-rtts']))
        elif dt == dts[-1]:
            buf.append(item['hop-num'] if subject == 'hop number' else statistics.mean(item['last-rtts']))
        else:
            if len(buf) == 0:
                dts[-1] = dt
                continue

            dts.append(dt)
            buf_arr = np.array(buf)
            
            if spec == 'min':
                stats_data.append(min(buf))
            elif spec == 'max':
                stats_data.append(max(buf))
            elif spec == 'avg':
                stats_data.append(int(np.mean(buf_arr)))
            else:
                q25, q50, q75 = np.percentile(buf_arr, [25, 50, 75])

                if spec == 'q25':
                    stats_data.append(int(q25))
                elif spec == 'q75':
                    stats_data.append(int(q75))
                elif spec == 'med':
                    stats_data.append(int(q50))
                else:
                    raise Exception('unimplemented statistics')
            buf = [item['hop-num']]

    if len(buf) > 0:
        buf_arr = np.array(buf)
        
        if spec == 'min':
            stats_data.append(min(buf))
        elif spec == 'max':
            stats_data.append(max(buf))
        elif spec == 'avg':
            stats_data.append(int(np.mean(buf_arr)))
        else:
            q25, q50, q75 = np.percentile(buf_arr, [25, 50, 75])

            if spec == 'q25':
                stats_data.append(int(q25))
            elif spec == 'q75':
                stats_data.append(int(q75))
            elif spec == 'med':
                stats_data.append(int(q50))
            else:
                raise Exception('unimplemented statistics')

    return sorted(list(dates)), dts, stats_data


def parse_iplink(raw_data, mode='top_k', top_r=5, top_k=5):
    
    stats, aggre = {}, set()
    counter = {}

    for k, v in raw_data.items():
        dt = datetime.strptime(k, '%y-%m-%d').replace(tzinfo=None)
        for item in v:
            stats.setdefault(item['node'], {})
            stats[item['node']][dt] = item['count']

        sorted_node = sorted(v, key=lambda x : x['count'], reverse=True)
        if mode == 'top_k':
            sorted_node = sorted_node[:top_k]
        elif mode == 'top_r':
            num_extracted = int(len(sorted_node) * top_r / 100)
            sorted_node = sorted_node[:num_extracted]
        
        for item in sorted_node:
            aggre.add(item['node'])
            counter[item['node']] = counter.get(item['node'], 0) + item['count']

    aggre = [inst for inst in list(aggre) if counter.get(inst, 0) > 5]
    aggre = sorted(list(aggre), key=lambda x : counter[x], reverse=True)

    return stats, aggre
