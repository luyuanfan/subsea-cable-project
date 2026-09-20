"""
This program (given pre-filtered files for the queried source and destination locations):
(1) Read one {month}_{vp}2{dst}.jsonl.gz file. 
(2) Store and annotate all traceroute records with its:
    - Time (datetime)
    - Round trip time (last-rtts)
    - Number of hops (hop-num)
    - Between which two ASNs (crosscn-asn)
"""
import re
import json
import gzip
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--in_path', type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    args = parser.parse_args()

    data_aggre = []
    with gzip.open(args.in_path, 'rt', encoding='utf-8') as f:
        for line in f:
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                break

            for item in value:
                if item['stop-reason'] != 'completed':
                    continue

                dt = item['start-ts']
                rtts = [i['rtt'] for i in item['hop-metas'][-3:]]
                hop_num = item['stop-hop']
                crosscn_asns = item['crosscn-asn']

                data_aggre.append({
                    'datetime': dt,
                    'last-rtts': rtts,
                    'hop-num' : hop_num,
                    'crosscn-asns': crosscn_asns
                })

    data_aggre.sort(key = lambda x : x['datetime'])

    tmp_path = args.out_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(data_aggre, f, indent=4)
    os.replace(tmp_path, args.out_path)