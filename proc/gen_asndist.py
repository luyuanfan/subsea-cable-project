"""
This program computes how much each ASN contributes to the total number of traces. 
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

    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    asndist_dict = {}

    with gzip.open(args.in_path, 'rt', encoding='utf-8') as f:
        for line in f:
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                break 
            re_date = date_pattern.search(key)
            label = f"{re_date.group(2)}-{re_date.group(3)}-{re_date.group(4)}"
            asndist_dict.setdefault(label, {'counter': 0, 'asn-dist': {}})
            for inst in value:
                asndist_dict[label]['counter'] += 1
                for asn in inst['crosscn-asn']:
                    asndist_dict[label]['asn-dist'][asn] = asndist_dict[label]['asn-dist'].get(asn, 0) + 1
    
    for k, v in asndist_dict.items():
        total_asn_counts = sum(list(v['asn-dist'].values()))
        v['asn-dist'] = { k : v / total_asn_counts for k, v in v['asn-dist'].items()}

    with open(args.out_path, 'w') as f:
        json.dump(asndist_dict, f, indent=4)
