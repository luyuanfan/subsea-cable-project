"""
This program:
(1) Reads files from data/buf/ by country;
(2) Finds every possible country to country pairs;
(3) Execute functions in proc/ for each pair. 
"""
import re
import os
import sys
import argparse
import subprocess

import pandas as pd

ROOT_DIR = 'data'
DATA_DIR = 'example-buf'
STATS_DIR = 'example-stats'
ISO_PATH = 'data/iso-3166-countries-with-regional-codes.csv'
PROC_DIR = 'proc'

SUBDIRS = ['probe-filter', 'outputs', 'graphs', 'asn-dist', 'prelim']
STEPS = [
    ('2',   'preliminary data',         'proc/gen_prelim',     '--out_path', 'prelim/{tag}.json',               []),
    ('3.1', 'node-based graph data',    'proc/gen_tracegraph', '--out_dir',  'outputs/{tag}_node.json',         []),
    ('3.2', 'edge-based graph data',    'proc/gen_tracegraph', '--out_dir',  'outputs/{tag}_edge.json',         ['--target', 'edge']),
    ('4',   'graph visual data',        'proc/gen_tracegraph', '--out_dir',  'graphs/{tag}',                    ['--out_format', 'xml']),
    ('5',   'cross-cn edge graph data', 'proc/gen_crosscn',    '--out_path', 'outputs/{tag}_crosscn_edge.json', []),
    ('6',   'asn distribution data',    'proc/gen_asndist',    '--out_path', 'asn-dist/{tag}.json',             []),
]


def run_step(label, module, *args):
    try:
        subprocess.run(
            [sys.executable, f'{module}.py', *args],
            check=True, text=True, stderr=subprocess.PIPE, stdout=sys.stdout,
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f'Error running step {label}: \nstderr: {e.stderr}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, default=ROOT_DIR)
    parser.add_argument('--data_dir', type=str, default=DATA_DIR)
    parser.add_argument('--stats_dir', type=str, default=STATS_DIR)
    args = parser.parse_args()

    # create directory dependencies
    data_dir = f'{args.root_dir}/{args.data_dir}'
    stats_dir = f'{args.root_dir}/{args.stats_dir}'
    os.makedirs(stats_dir, exist_ok=True)
    os.makedirs(f'{stats_dir}/probe-filter', exist_ok=True)
    os.makedirs(f'{stats_dir}/outputs', exist_ok=True)
    os.makedirs(f'{stats_dir}/graphs', exist_ok=True)
    os.makedirs(f'{stats_dir}/asn-dist', exist_ok=True)
    os.makedirs(f'{stats_dir}/prelim', exist_ok=True)
    
    # map 2-letter ISO code to country name
    iso_data = pd.read_csv(ISO_PATH)
    iso_data = iso_data[~iso_data['alpha-2'].isna()]
    iso_data = iso_data[['name', 'alpha-2']]
    iso2cn = {
        iso_data.iloc[i]['alpha-2'].lower(): iso_data.iloc[i]['name']
        for i in range(len(iso_data))
    }

    # preprocess viewpoint metadata
    avail_vps = os.listdir(data_dir)
    vp_tokens = [vp.partition('-') for vp in avail_vps]
    avail_isos = [p[0] for p in vp_tokens]
    vp_specs = [p[2] for p in vp_tokens]
    unknown = [vp for vp, iso in zip(avail_vps, avail_isos) if iso not in iso2cn]
    assert not unknown, f'Unrecognized ISO code: {unknown}'
    avail_cns = [f'{iso2cn[iso]}[{spec}]' for iso, spec in zip(avail_isos, vp_specs)]
    print(f'Gathering data for available countries: {avail_cns}...')
    avail_isos = sorted(set(avail_isos))

    for d in SUBDIRS:
        os.makedirs(f'{stats_dir}/{d}', exist_ok=True)
    pf_dir = f'{stats_dir}/probe-filter'

    for vp, src_iso in zip(avail_vps, avail_isos):
        dst_isos = [dst for dst in avail_isos if dst != src_iso]
        vp_dir = f'{data_dir}/{vp}'
        
        for fname in sorted(os.listdir(vp_dir)):
            ym = fname.split('.')[0]

            queue_dst = [
                dst for dst in dst_isos
                if not os.path.exists(f'{pf_dir}/{ym}_{vp}2{dst}.jsonl.gz')
            ]
            if queue_dst:
                run_step('1', 'proc/aggre_geoloc',
                        '--in_path', f'{vp_dir}/{fname}',
                        '--out_prefix', f'{pf_dir}/{ym}_{vp}2',
                        '--dst', ','.join(queue_dst))
            print(f'Completed step 1, aggregating geoloc metadata on probes from {vp} to {queue_dst}')

            for dst_iso in dst_isos:
                tag = f'{ym}_{vp}2{dst_iso}'
                probe_path = f'{pf_dir}/{tag}.jsonl.gz'
                if not os.path.exists(probe_path):
                    continue

                for label, descpt, module, out_flag, out_tmpl, extras in STEPS:
                    out_path = f'{stats_dir}/{out_tmpl.format(tag=tag)}'
                    if not os.path.exists(out_path):
                        run_step(label, module, '--in_path', probe_path, out_flag, out_path, *extras)
                    print(f'Completed step {label}, {descpt} from {vp} to {dst_iso}. Skipping...')

    print("All done in prepare_metadata_pipeline")

if __name__ == '__main__':
    main()