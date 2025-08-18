import networkx as nx
import matplotlib.pyplot as plt
import argparse, gzip, json, re, os, copy
from tqdm import tqdm
import maxminddb as mmdb 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    args = parser.parse_args()
    
    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    json_dict, per_date_dict = {}, {}
    prev_label = None
    node2asn = {}
    
    with gzip.open(args.in_path, 'rt', encoding='utf-8') as f:
        for line in tqdm(f):
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                    break 

            re_date = date_pattern.search(key)
            label = f"{re_date.group(2)}-{re_date.group(3)}-{re_date.group(4)}"
            value = [inst for inst in value if inst['stop-reason'] == 'completed']
            if len(value) == 0:
                continue

            if prev_label and prev_label != label:
                json_dict[prev_label] = [{'node': key, 'count': value, 'asns': list(node2asn.get(key, set()))} for key, value in per_date_dict.items()] 
                per_date_dict = {} 

            prev_label = label

            for inst in value:
                iplinks = inst['crosscn-iplink']
                asns = inst['crosscn-asn']

                for link in iplinks:
                    per_date_dict[link] = per_date_dict.get(link, 0) + 1
                    node2asn.setdefault(link, set())
                    node2asn[link].update(asns)

    json_dict[label] = [{'node': key, 'count': value, 'asns': list(node2asn.get(key, set()))} for key, value in per_date_dict.items()] 
    with open(args.out_path, 'w') as f:
        json.dump(json_dict, f, indent=4)
