import os, json
from datetime import datetime

def aggre_avail_data(in_dir, in_suffix, start, end, data_type='dict list'):
    files = sorted([f for f in os.listdir(in_dir) if f.endswith(in_suffix)])
    start_month_str = start.strftime('%Y%m')
    end_month_str = end.strftime('%Y%m')
    start_day_str = start.strftime('%y-%m-%d')
    end_day_str = end.strftime('%y-%m-%d')
    
    lev1_type, lev2_type = data_type.split()[0], data_type.split()[1]
    json_data = {} if lev1_type == 'dict' else []
    
    asn_counter = {}
    for f in files:
        if f[:6] < start_month_str or f[:6] > end_month_str:
            continue
        with open(os.path.join(in_dir, f), 'r') as in_f:
            raw_json = json.load(in_f)

            if lev1_type == 'dict':
                for k, v in raw_json.items():
                    if k < start_day_str or k > end_day_str:
                        continue
                    json_data[k] = v
                    if lev2_type == 'list':
                        for inst in v:
                            for asn in inst.get('asns', []):
                                asn_counter[asn] = asn_counter.get(asn, 0) + inst.get('count', 0)
                    elif lev2_type == 'dict':
                        for asn, c in v.get('asn-dist', {}).items():
                            asn_counter[asn] = asn_counter.get(asn, 0) + c

            elif lev1_type == 'list':
                for inst in raw_json:
                    date_str = datetime.strptime(inst['datetime'], '%Y-%m-%d %H:%M:%S.%f%z').strftime('%y-%m-%d')
                    if date_str < start_day_str or date_str > end_day_str:
                        continue
                    json_data.append(inst)
                    
                    if lev2_type == 'dict':
                        for asn in inst['crosscn-asns']:
                            asn_counter[asn] = asn_counter.get(asn, 0) + 1
        
    asn_sorted = dict(sorted(asn_counter.items(), key=lambda x : x[1], reverse=True))

    return json_data, list(asn_sorted.keys())[:30]

def filter_avail_data(json_data, asn_filters, data_type='dict'):
    if not asn_filters or len(asn_filters) == 0:
        return json_data
    
   
    filtered_json_data = {} if data_type == 'dict' else []

    if data_type == 'dict':
        for k, v in json_data.items():
            filtered_v = []
            for inst in v:
                if any(asn in inst['asns'] for asn in asn_filters):
                    filtered_v.append(inst)
            filtered_json_data[k] = filtered_v
    else:
        for inst in json_data:
            if any(asn in inst['crosscn-asns'] for asn in asn_filters):
                filtered_json_data.append(inst)

    return filtered_json_data
