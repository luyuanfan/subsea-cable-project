"""
This program:
(1) Reads files from data/buf/ by country;
(2) Finds every possible country to country pairs;
(3) Execute functions in proc/ for each pair. 
"""
import os
import sys
import argparse
import subprocess

import pandas as pd

from config import ROOT_DIR, ARK_BUF_DIR, STATS_DIR, ISO_FPATH


SUBDIRS = ["probe-filter", "outputs", "graphs", "asn-dist", "prelim"]
STEPS = [
    ("2",   "preliminary data",         "proc.gen_prelim",     "--out_path", "prelim/{tag}.json",               []),
    ("3.1", "node-based graph data",    "proc.gen_tracegraph", "--out_dir",  "outputs/{tag}_node.json",         []),
    ("3.2", "edge-based graph data",    "proc.gen_tracegraph", "--out_dir",  "outputs/{tag}_edge.json",         ["--target", "edge"]),
    ("4",   "graph visual data",        "proc.gen_tracegraph", "--out_dir",  "graphs/{tag}",                    ["--out_format", "xml"]),
    ("5",   "cross-cn edge graph data", "proc.gen_crosscn",    "--out_path", "outputs/{tag}_crosscn_edge.json", []),
    ("6",   "asn distribution data",    "proc.gen_asndist",    "--out_path", "asn-dist/{tag}.json",             []),
]


def run_step(label, module, *args):
    try:
        subprocess.run(
            [sys.executable, "-m", module, *args],
            check=True, text=True, stderr=subprocess.PIPE, stdout=sys.stdout,
            cwd=ROOT_DIR, 
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error running step {label}: \nstderr: {e.stderr}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default=ARK_BUF_DIR)
    parser.add_argument("--output_dir", type=str, default=STATS_DIR)
    args = parser.parse_args()

    input_dir = f"{args.input_dir}"
    output_dir = f"{args.output_dir}"
    os.makedirs(output_dir, exist_ok=True)
    for sd in SUBDIRS:
        os.makedirs(f"{output_dir}/{sd}", exist_ok=True)
    pf_dir = f"{output_dir}/probe-filter"

    iso_data = pd.read_csv(ISO_FPATH, keep_default_na=False, na_values=[""])
    iso_data = iso_data[~iso_data["alpha-2"].isna()]
    iso2cn = {
        iso_data.iloc[i]["alpha-2"].lower(): iso_data.iloc[i]["name"]
        for i in range(len(iso_data))
    }

    avail_vps = sorted(
        vp for vp in os.listdir(input_dir)
        if os.path.isdir(f"{input_dir}/{vp}")
    )
    vp_tokens = [vp.partition("-") for vp in avail_vps]
    vp_isos = [p[0] for p in vp_tokens]
    vp_specs = [p[2] for p in vp_tokens]
    unknown = [vp for vp, iso in zip(avail_vps, vp_isos) if iso not in iso2cn]
    assert not unknown, f"Unrecognized ISO code: {unknown}"
    avail_cns = [f"{iso2cn[iso]}[{spec}]" for iso, spec in zip(vp_isos, vp_specs)]
    print(f"Gathering data for available countries: {avail_cns}...")
    all_isos = sorted(set(vp_isos)) 

    for vp, src_iso in zip(avail_vps, vp_isos):
        dst_isos = [dst for dst in all_isos if dst != src_iso]
        vp_dir = f"{input_dir}/{vp}"
        
        for fname in sorted(os.listdir(vp_dir)):
            ym = fname.split(".")[0]

            queue_dst = [
                dst for dst in dst_isos
                if not os.path.exists(f"{pf_dir}/{ym}_{vp}2{dst}.jsonl.gz")
            ]
            if queue_dst:
                run_step("1", "proc.aggre_geoloc",
                        "--in_path", f"{vp_dir}/{fname}",
                        "--out_prefix", f"{pf_dir}/{ym}_{vp}2",
                        "--dst", ",".join(queue_dst))
                print(f"Completed step 1, aggregating geoloc metadata on probes from {vp} to {queue_dst}")
            else:
                print(f"Skipping step 1, geoloc metadata from {vp} ({ym}) already aggregated")

            for dst_iso in dst_isos:
                tag = f"{ym}_{vp}2{dst_iso}"
                probe_path = f"{pf_dir}/{tag}.jsonl.gz"
                if not os.path.exists(probe_path):
                    continue

                for label, descpt, module, out_flag, out_tmpl, extras in STEPS:
                    out_path = f"{output_dir}/{out_tmpl.format(tag=tag)}"
                    if os.path.exists(out_path):
                        print(f"Skipping step {label}, {descpt} from {vp} to {dst_iso}")
                        continue
                    run_step(label, module, "--in_path", probe_path, out_flag, out_path, *extras)
                    print(f"Completed step {label}, {descpt} from {vp} to {dst_iso}")

    print("All done in prepare_metadata_pipeline")

if __name__ == "__main__":
    main()