import argparse, subprocess, os, sys, re
import pandas as pd

SUBDIRS = ['probe-filter', 'outputs', 'graphs', 'asn-dist', 'prelim']
STEPS = [
    ('2',   'preliminary data',         'proc.gen_prelim',     '--out_path', 'prelim/{tag}.json',               []),
    ('3.1', 'node-based graph data',    'proc.gen_tracegraph', '--out_dir',  'outputs/{tag}_node.json',         []),
    ('3.2', 'edge-based graph data',    'proc.gen_tracegraph', '--out_dir',  'outputs/{tag}_edge.json',         ['--target', 'edge']),
    ('4',   'graph visual data',        'proc.gen_tracegraph', '--out_dir',  'graphs/{tag}',                    ['--out_format', 'xml']),
    ('5',   'cross-cn edge graph data', 'proc.gen_crosscn',    '--out_path', 'outputs/{tag}_crosscn_edge.json', []),
    ('6',   'asn distribution data',    'proc.gen_asndist',    '--out_path', 'asn-dist/{tag}.json',             []),
]

def run_step(label, module, *args):
    try:
        subprocess.run(
            [sys.executable, '-m', module, *args],
            check=True, text=True, stderr=subprocess.PIPE, stdout=sys.stdout,
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f'Error running step {label}: \nstderr: {e.stderr}')

def main():
    """
    TODO: 
    """
    # create cmdline parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, default='data')
    parser.add_argument('--data_dir', type=str, default='buf')
    parser.add_argument('--stats_dir', type=str, default='north-europe-meta')
    parser.add_argument('--iso_db', type=str, default='data/iso-3166-countries-with-regional-codes.csv')
    args = parser.parse_args()

    # create pipeline directories based on cmdline
    data_dir = f'{args.root_dir}/{args.data_dir}'
    stats_dir = f'{args.root_dir}/{args.stats_dir}'
    os.makedirs(stats_dir, exist_ok=True)
    os.makedirs(f'{stats_dir}/probe-filter', exist_ok=True)
    os.makedirs(f'{stats_dir}/outputs', exist_ok=True)
    os.makedirs(f'{stats_dir}/graphs', exist_ok=True)
    os.makedirs(f'{stats_dir}/asn-dist', exist_ok=True)
    os.makedirs(f'{stats_dir}/prelim', exist_ok=True)
    
    # map 2-letter ISO code to country name
    iso_data = pd.read_csv(args.iso_db)
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

    # for curr_iso in avail_vps:

    #     meta_geodata_dir = f'{data_dir}/{curr_iso}'
    #     probe_filter_dir = f'{stats_dir}/probe-filter'

    #     avail_dst = [dst for dst in avail_isos if dst != curr_iso]

    #     for month_file in os.listdir(meta_geodata_dir):
    #         meta_geodata_path = f'{meta_geodata_dir}/{month_file}'
    #         month_spec = month_file.split('.')[0]

    #         # step 1: aggregate geoloc data
    #         q_dst = [dst for dst in avail_dst if not os.path.exists(f'{probe_filter_dir}/{month_spec}_{curr_iso}2{dst}.jsonl.gz')]
    #         if len(q_dst) == 0:
    #             print(f'completed step 1, aggregating geoloc metadata on probes from {curr_iso} to {q_dst}. skipping...')
    #         else:
    #             print(f'step 1: aggregating geoloc metadata on probes from {curr_iso} to {q_dst}')
    #             try:
    #                 result = subprocess.run([
    #                     'python', '-m', 'proc.aggre_geoloc',
    #                     '--in_path', meta_geodata_path,
    #                     '--out_prefix', f'{probe_filter_dir}/{month_spec}_{curr_iso}2',
    #                     '--dst', ','.join(q_dst),
    #                     ],
    #                     check=True, 
    #                     text=True, 
    #                     stderr=subprocess.PIPE, 
    #                     stdout=sys.stdout
    #                 )

    #             except subprocess.CalledProcessError as e:
    #                 print(f'error running step 1: the script exited with a non-zero status code {e.returncode}')
    #                 print(f'stderr: {e.stderr}')
    #                 exit(-1)

    #             except Exception as e:
    #                 print(f'receiving exception when running step 1: {str(e)}')
    #                 exit(-1)

    #         for dst in avail_dst:
    #             prefix = f'{curr_iso}2{dst}'
    #             probe_filter_path = f'{probe_filter_dir}/{month_spec}_{prefix}.jsonl.gz'
    #             prelim_dir = f'{stats_dir}/prelim'
    #             prelim_path = f'{prelim_dir}/{month_spec}_{prefix}.json'

    #             graph_json_dir = f'{stats_dir}/outputs'
    #             graph_node_path = f'{graph_json_dir}/{month_spec}_{prefix}_node.json'
    #             graph_edge_path = f'{graph_json_dir}/{month_spec}_{prefix}_edge.json'
    #             graph_crosscn_path = f'{graph_json_dir}/{month_spec}_{prefix}_crosscn_edge.json'
    #             graph_vis_dir = f'{stats_dir}/graphs/{month_spec}_{prefix}'

    #             asndist_dir = f'{stats_dir}/asn-dist'
    #             asndist_path = f'{asndist_dir}/{month_spec}_{prefix}.json'

    #             if not os.path.exists(probe_filter_path):
    #                 # data not available between the two countries
    #                 continue
                
    #             # step 2: generate preliminary data
    #             if os.path.exists(prelim_path):
    #                 print(f'completed step 2, generate preliminary data from {curr_iso} to {dst}. skipping...')
    #             else:
    #                 print(f'step 2: generating preliminary data from {curr_iso} to {dst}')
    #                 try:
    #                     subprocess.run([
    #                         'python', '-m', 'proc.gen_prelim',
    #                         '--in_path', probe_filter_path,
    #                         '--out_path', prelim_path
    #                         ],
    #                         check=True, 
    #                         text=True, 
    #                         stderr=subprocess.PIPE, 
    #                         stdout=sys.stdout
    #                     )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 2: {str(e)}')
    #                     exit(-1)

    #             # step 3: generate traceroute graph json on IP and IP link
    #             if os.path.exists(graph_node_path):
    #                 print(f'completed step 3.1, generating node(ip address)-based graph data from {curr_iso} to {dst}. skipping...')
    #             else:
    #                 print(f'step 3.1: generating node(ip address)-based graph data from {curr_iso} to {dst}.')
    #                 try:
    #                     subprocess.run([
    #                         'python', '-m', 'proc.gen_tracegraph',
    #                         '--in_path', probe_filter_path,
    #                         '--out_dir', graph_node_path
    #                         ],
    #                         check=True, 
    #                         text=True, 
    #                         stderr=subprocess.PIPE, 
    #                         stdout=sys.stdout
    #                     )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 3.1: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 3.1: {str(e)}')
    #                     exit(-1)

    #             if os.path.exists(graph_edge_path):
    #                 print(f'completed step 3.2, creating edge(path link pair)-based graph data from {curr_iso} to {dst}. skipping...')
    #             else:
    #                 print(f'step 3.2, create edge(path link pair)-based graph data from {curr_iso} to {dst}.')
    #                 try:
    #                     subprocess.run([
    #                         'python', '-m', 'proc.gen_tracegraph',
    #                         '--in_path', probe_filter_path,
    #                         '--out_dir', graph_edge_path,
    #                         '--target', 'edge',
    #                         ],
    #                         check=True,
    #                         text=True,
    #                         stderr=subprocess.PIPE,
    #                         stdout=sys.stdout,
    #                         )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 3.2: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 3.2: {str(e)}')
    #                     exit(-1)
                
    #             # step 4: generate graph visuals
    #             if os.path.exists(graph_vis_dir):
    #                 print(f'completed step 4, generating graph visual data from {curr_iso} to {dst}. skipping...')
    #             else:
    #                 print(f'step 4: generating graph visual data from {curr_iso} to {dst}.')
    #                 try:
    #                     subprocess.run([
    #                         'python', '-m', 'proc.gen_tracegraph',
    #                         '--in_path', probe_filter_path,
    #                         '--out_dir', graph_vis_dir,
    #                         '--out_format', 'xml'
    #                         ],
    #                         check=True, 
    #                         text=True, 
    #                         stderr=subprocess.PIPE, 
    #                         stdout=sys.stdout
    #                 )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 4: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 4: {str(e)}')
    #                     exit(-1)

    #             # step 5: generate traceroute graph on cross-cn link
    #             if os.path.exists(graph_crosscn_path):
    #                 print(f'completed step 5, generating cross-cn edge(path link pair)-based graph data from {curr_iso} to {dst}. skipping...')
    #             else:
    #                 print(f'step 5: generating cross-cn edge(path link pair)-based graph data from {curr_iso} to {dst}.')
    #                 try:
    #                     subprocess.run([
    #                         'python', '-m', 'proc.gen_crosscn',
    #                         '--in_path', probe_filter_path,
    #                         '--out_path', graph_crosscn_path,
    #                         ],
    #                         check=True,
    #                         text=True,
    #                         stderr=subprocess.PIPE,
    #                         stdout=sys.stdout
    #                         )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 5: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 5: {str(e)}')
    #                     exit(-1)

    #             # step 6: generate asn distribution data for specified dst cns
    #             if os.path.exists(asndist_path):
    #                 print(f'completed step 6, generating asn distribution data from {curr_iso} to {avail_dst}. skipping...')
    #             else:
    #                 print(f'step 6: generating asn distribution data from {curr_iso} to {dst}')
    #                 try:
    #                     result = subprocess.run([
    #                         'python', '-m', 'proc.gen_asndist',
    #                         '--in_path', probe_filter_path,
    #                         '--out_path', asndist_path,
    #                         ],
    #                         check=True, 
    #                         text=True, 
    #                         stderr=subprocess.PIPE, 
    #                         stdout=sys.stdout
    #                     )

    #                 except subprocess.CalledProcessError as e:
    #                     print(f'error running step 6: the script exited with a non-zero status code {e.returncode}')
    #                     print(f'stderr: {e.stderr}')
    #                     exit(-1)

    #                 except Exception as e:
    #                     print(f'receiving exception when running step 6: {str(e)}')
    #                     exit(-1)
    
    for d in SUBDIRS:
        os.makedirs(f'{stats_dir}/{d}', exist_ok=True)
    pf_dir = f'{stats_dir}/probe-filter'

    for vp, src_iso in zip(avail_vps, avail_isos):
        dst_isos = [dst for dst in avail_isos if dst != src_iso]
        vp_dir = f'{data_dir}/{vp}'
        
        for month_file in sorted(os.listdir(vp_dir)):
            month = month_file.split('.')[0]

            queue_dst = [
                dst for dst in dst_isos
                if not os.path.exists(f'{pf_dir}/{month}_{vp}2{dst}.jsonl.gz')
            ]
            if queue_dst:
                print(f'Step 1: aggregating geoloc metadata on probes from {vp} to {queue_dst}')
                run_step('1', 'proc.aggre_geoloc',
                        '--in_path', f'{vp_dir}/{month_file}',
                        '--out_prefix', f'{pf_dir}/{month}_{vp}2',
                        '--dst', ','.join(queue_dst))
            else:
                print(f"Completed step 1, aggregating geoloc metadata on probes from {vp} to {dst_isos}.")

            for dst_iso in dst_isos:
                tag = f'{month}_{vp}2{dst_iso}'
                probe_path = f'{pf_dir}/{tag}.jsonl.gz'
                if not os.path.exists(probe_path):
                    continue

                for label, descpt, module, out_flag, out_tmpl, extras in STEPS:
                    out_path = f'{stats_dir}/{out_tmpl.format(tag=tag)}'
                    if os.path.exists(out_path):
                        print(f'Completed step {label}, {descpt} from {vp} to {dst_iso}. Skipping...')
                        continue
                    print(f'Step {label}: {descpt} from {vp} to {dst_iso}')
                    run_step(label, module, '--in_path', probe_path, out_flag, out_path, *extras)

if __name__ == '__main__':
    main()