"""
All Ark probing data must already be present in ARK_DIR.

ARK_DIR has cycle directories looking like: 
    cycle-2024021/  cycle-20240303/  cycle-20240320/

Each cycle directory has the files looking like:
    abz2-uk.team-probing.c011242.20240130.warts.gz
    eug-us.team-probing.c011242.20240130.warts.gz
    ory4-fr.team-probing.c011244.20240130.warts.gz
<airport_name><optional_probe_num>-<iso_code>.team-probing.*.warts.gz

This program:
(1) Looks through all file names in ARK_DIR;
(2) Picks the files relevant to the current query (country, airport, probe_num);
(3) Groups them and sort them by (year, month);
(4) Copys them to data/aggre-data for future processing. 
"""

import os
import sys
import re
import argparse
import gzip
import json
import logging
from collections import defaultdict

from config import ARK_DIR, ARK_BUF_DIR, START_TIME, END_TIME
from remote.parser import WartsDumpParser


_DATE = re.compile(r"\d{8}")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def search_date(fname):
    """
    Search for YYYYMMDD in a filename, return date. 
    'cycle-20240101' -> '20240101'
    """
    m = _DATE.search(fname)
    return m.group() if m else None


def build_vp_name(country, airport, probe_num):
    """
    Build output filename based on (country, airport, probe_num) spec.
    ('gh') -> 'gh' 
    ('de', 'muc') -> 'de-muc'
    ('fr', 'cdg', 3) -> 'fr-cdg-3'
    """
    parts = [country]
    if airport:
        parts.append(airport)
    if probe_num:
        parts.append(str(probe_num))
    return "-".join(parts)


def build_regex_label(country, airport, probe_num):
    """
    Build regex pattern based on (country, airport, probe_num) spec, such as:
        abz1-uk.team-probing
        abz-uk.team-probing
        uk.team-probing
    Return regex object. 

    When probe_num is not provided or is -1, regex matches for every probe_num within
    that airport.
    """
    if not airport:
        return re.compile(rf"{country}\.team-probing")
    else:
        if not probe_num:
            return re.compile(rf"{airport}\d*-{country}\.team-probing")
        else:
            return re.compile(rf"{airport}{probe_num}-{country}\.team-probing")


def sort_cycle_by_ym(data_dir, start, end):
    """
    Produce a dictionary in the following structure: 
    {
        (202401) -> [20240101, 20240115, 20240131]
        (202411) -> [20241101, 20241115]
    }
    Key YYYYMM ascends chronologically. 
    """
    cycle_names = [
        n for n in os.listdir(data_dir)
        if search_date(n) and os.path.isdir(os.path.join(data_dir, n))
    ]
    months = defaultdict(list)
    for name in sorted(cycle_names, key=search_date):
        ym = search_date(name)[:6]
        if start <= ym <= end:
            months[ym].append(name)
    return dict(months)
    

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default=ARK_DIR)
    parser.add_argument("--output_dir", type=str, default=ARK_BUF_DIR)
    parser.add_argument("--country", type=str, required=True)
    parser.add_argument("--airport", type=str, default=None)
    parser.add_argument("--probe_id", type=int, default=None)
    parser.add_argument("--start_time", type=str, default=START_TIME)
    parser.add_argument("--end_time", type=str, default=END_TIME)
    parser.add_argument("--threshold", type=int, default=15)
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        logger.debug(f"Input directory [{args.input_dir}] does not exist. Exiting...")
        sys.exit(1)
    if args.probe_id and not args.airport:
        logger.debug(f"Airport specified but no probe number provided. Exiting...")
        sys.exit(1)

    label = build_regex_label(args.country, args.airport, args.probe_id)
    vp_name = build_vp_name(args.country, args.airport, args.probe_id)
    output_dir = os.path.join(args.output_dir, vp_name)

    for ym, cycles in sort_cycle_by_ym(args.input_dir, args.start_time, args.end_time).items():
        if len(cycles) < args.threshold:
            print(f"{ym} {vp_name} has only {len(cycles)} cycles (minimum {args.threshold}. Skipping...")
            continue

        fout_path = os.path.join(output_dir, f"{ym}.jsonl.gz")
        if os.path.exists(fout_path):
            print(f"{fout_path} already exists. Skipping...")
            continue

        jobs = [
            (cycle, fpath)
            for cycle in cycles
                for fpath in sorted(os.listdir(os.path.join(args.input_dir, cycle)))
                    if label.search(fpath)
        ]
        if not jobs:
            print(f"{ym} {vp_name} has no matching probing instances. Skipping...")
            continue

        print(f"{ym}: {len(jobs)} probing instances over {len(cycles)} cycles.")
        os.makedirs(output_dir, exist_ok=True)

        tmp_path = os.path.join(args.output_dir, f".{vp_name}-{ym}.tmp")
        with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
            for cycle, fpath in jobs:
                print(f"Querying capture {fpath}")
                src_path = os.path.join(args.input_dir, cycle)
                p = WartsDumpParser(src_path, fpath)
                f.write(json.dumps({fpath: p.get_data("trace")}) + "\n")

        os.replace(tmp_path, fout_path)

    print("All done in aggregate_raw_measurement")

if __name__ == "__main__":
    main()