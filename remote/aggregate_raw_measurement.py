"""
All Ark data must be present in ARK_DIR.

ARK_DIR has cycle directories looking like: 
    cycle-2024021/  cycle-20240303/  cycle-20240320/

Each cycle directory has the files looking like:
    abz2-uk.team-probing.c011242.20240130.warts.gz
    eug-us.team-probing.c011242.20240130.warts.gz
    ory4-fr.team-probing.c011244.20240130.warts.gz

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

from parser import WartsDumpParser

ARK_DIR = "/data/topology/ark/data/team-probing/list-7.allpref24/team-1/daily/2024"

_DATE = re.compile(r"\d{8}")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def cycle_date(name: str):
    """
    cycle-20240101" -> "20240101";
    None if the name has no date.
    """
    m = _DATE.search(name)
    return m.group() if m else None


def out_name(country, airport, probe_num):
    """
    ('de', 'muc', -1) -> 'de-muc--1'
    """
    parts = [country]
    if airport:
        parts.append(airport)
    if probe_num:
        parts.append(str(probe_num))
    return "-".join(parts)


def build_label(country, airport, probe_num):
    """
    Search for pattern like:
        abz*-uk.team-probing
        uk.team-probing
    """
    if not airport:
        return re.compile(rf"{country}\.team-probing")
    elif airport and not probe_num:
        return re.compile(rf"{airport}\d*-{country}\.team-probing")
    elif airport and probe_num:
        num = "" if probe_num == -1 else probe_num
        return re.compile(rf"{airport}{num}-{country}\.team-probing")


def cycles_by_month(directory, start, end):
    """
    Produce a dictionary in the following structure: 
    {
        (202401) -> [20240101, 20240115, 20240131]
        (202411) -> [20241101, 20241115]
    }
    Key (year, month) ascends. 
    """
    names = [
        n for n in os.listdir(directory)
        if cycle_date(n) and os.path.isdir(os.path.join(directory, n))
    ]
    months = defaultdict(list)
    for name in sorted(names, key=cycle_date):
        ym = cycle_date(name)[:6]
        if start <= ym <= end:
            months[ym].append(name)
    return dict(month)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default=ARK_DIR)
    parser.add_argument("--out_dir", type=str, default="data/aggre-data")
    parser.add_argument("--country_spec", type=str, required=True)
    parser.add_argument("--airport_spec", type=str, default=None)
    parser.add_argument("--probe_num_spec", type=int, default=None)
    parser.add_argument("--start_time", type=str, default="202401")
    parser.add_argument("--end_time", type=str, default="202412")
    parser.add_argument("--threshold", type=int, default=15)
    args = parser.parse_args()

    if not os.path.exists(args.in_dir):
        logger.debug(f"Input directory: [{args.in_dir}] does not exist.")
        sys.exit(1)
    if args.airport_spec and not args.probe_num_spec:
        logger.debug(f"Airport specified but not probe number.")
        sys.exit(1)

    label = build_label(args.country_spec, args.airport_spec, args.probe_num_spec)
    vp_name = out_name(args.country_spec, args.airport_spec, args.probe_num_spec)
    out_dir = os.path.join(args.out_dir, vp_name)

    for ym, cycles in cycles_by_month(args.in_dir, args.start_time, args.end_time).items():
        if len(cycles) < args.threshold:
            print(f"{ym} has only {len(cycles)} cycles (minimum {args.threshold}. Skipping...")
            continue

        out_path = os.path.join(out_dir, f"{ym}.jsonl.gz")
        if os.path.exists(out_path):
            print(f"{out_path} already exists. Skipping...")
            continue

        jobs = [(c, inst) for c in cycles
                for inst in sorted(os.listdir(os.path.join(args.in_dir, c)))
                if label.search(inst)]
        if not jobs:
            print(f"{ym}: no matching probing instances. Skipping...")
            continue

        print(f"{ym}: {len(jobs)} probing instances over {len(cycles)} cycles")
        os.makedirs(out_dir, exist_ok=True)

        tmp_path = os.path.join(args.out_dir, f".{vp_name}-{ym}.tmp")
        with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
            for cycle, inst in jobs:
                print(f"Querying capture {inst}")
                p = WartsDumpParser(os.path.join(args.in_dir, cycle), inst)
                f.write(json.dumps({inst: p.get_data("trace")}) + "\n")

        os.replace(tmp_path, out_path)

if __name__ == "__main__":
    main()