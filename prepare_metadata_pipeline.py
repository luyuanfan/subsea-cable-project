import argparse, subprocess, os, sys, re
import pandas as pd

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, default='data')
    parser.add_argument('--data_dir', type=str, default='buf')
    parser.add_argument('--stats_dir', type=str, default='north-europe-meta')
    parser.add_argument('--iso_db', type=str, default='data/iso-3166-countries-with-regional-codes.csv')
    args = parser.parse_args()
    
    # process iso data
    iso_data = pd.read_csv(args.iso_db)
    iso_data = iso_data[~iso_data['alpha-2'].isna()]
    iso_data = iso_data[['name', 'alpha-2']]
    iso2cn = {iso_data.iloc[i]['alpha-2'].lower(): iso_data.iloc[i]['name'] for i in range(len(iso_data))}
    cn2iso = {v : k for k, v in iso2cn.items()}

    data_dir = f'{args.root_dir}/{args.data_dir}'
    stats_dir = f'{args.root_dir}/{args.stats_dir}'

    avail_vps = [vp for vp in os.listdir(data_dir)]
    avail_isos = [vp.split('-')[0] for vp in avail_vps]
    vp_specs = [(vp.split('-')[1] if len(vp.split('-')) > 1 else '') for vp in avail_vps]
    avail_cns = [f'{iso2cn[iso]}[{vp_spec}]' for iso, vp_spec in zip(avail_isos, vp_specs) if iso2cn.get(iso, None)]
    assert(len(avail_isos) == len(avail_cns))
    print(f'gathering data for available countries: {avail_cns}')
    avail_isos = list(set(avail_isos))

    os.makedirs(stats_dir, exist_ok=True)

    os.makedirs(f'{stats_dir}/probe-filter', exist_ok=True)
    os.makedirs(f'{stats_dir}/outputs', exist_ok=True)
    os.makedirs(f'{stats_dir}/graphs', exist_ok=True)
    os.makedirs(f'{stats_dir}/asn-dist', exist_ok=True)
    os.makedirs(f'{stats_dir}/prelim', exist_ok=True)

    for vp_idx in range(len(avail_vps)):
        vp = avail_vps[vp_idx]
        avail_dst = [dst for dst in avail_isos if dst != vp.split('-')[0]]

        meta_geodata_dir = f'{data_dir}/{vp}'
        probe_filter_dir = f'{stats_dir}/probe-filter'

        for month_file in os.listdir(meta_geodata_dir):
            meta_geodata_path = f'{meta_geodata_dir}/{month_file}'
            month_spec = month_file.split('.')[0]

            # step 1: aggregate geoloc data
            q_dst = [dst for dst in avail_dst if not os.path.exists(f'{probe_filter_dir}/{month_spec}_{vp}2{dst}.jsonl.gz')]
            if len(q_dst) == 0:
                print(f'completed step 1, aggregating geoloc metadata on probes from {vp} to {q_dst}. skipping...')
            else:
                print(f'step 1: aggregating geoloc metadata on probes from {vp} to {q_dst}')
                try:
                    result = subprocess.run([
                        'python', '-m', 'proc.aggre_geoloc',
                        '--in_path', meta_geodata_path,
                        '--out_prefix', f'{probe_filter_dir}/{month_spec}_{vp}2',
                        '--dst', ','.join(q_dst),
                        ],
                        check=True, 
                        text=True, 
                        stderr=subprocess.PIPE, 
                        stdout=sys.stdout
                    )

                except subprocess.CalledProcessError as e:
                    print(f'error running step 1: the script exited with a non-zero status code {e.returncode}')
                    print(f'stderr: {e.stderr}')
                    exit(-1)

                except Exception as e:
                    print(f'receiving exception when running step 1: {str(e)}')
                    exit(-1)

            for dst in avail_dst:
                prefix = f'{vp}2{dst}'
                probe_filter_path = f'{probe_filter_dir}/{month_spec}_{prefix}.jsonl.gz'
                prelim_dir = f'{stats_dir}/prelim'
                prelim_path = f'{prelim_dir}/{month_spec}_{prefix}.json'

                graph_json_dir = f'{stats_dir}/outputs'
                graph_node_path = f'{graph_json_dir}/{month_spec}_{prefix}_node.json'
                graph_edge_path = f'{graph_json_dir}/{month_spec}_{prefix}_edge.json'
                graph_crosscn_path = f'{graph_json_dir}/{month_spec}_{prefix}_crosscn_edge.json'
                graph_vis_dir = f'{stats_dir}/graphs/{month_spec}_{prefix}'

                asndist_dir = f'{stats_dir}/asn-dist'
                asndist_path = f'{asndist_dir}/{month_spec}_{prefix}.json'

                if not os.path.exists(probe_filter_path):
                    # data not available between the two countries
                    continue
                
                # step 2: generate preliminary data
                if os.path.exists(prelim_path):
                    print(f'completed step 2, generate preliminary data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 2: generating preliminary data from {vp} to {dst}')
                    try:
                       subprocess.run([
                           'python', '-m', 'proc.gen_prelim',
                           '--in_path', probe_filter_path,
                           '--out_path', prelim_path
                           ],
                           check=True, 
                           text=True, 
                           stderr=subprocess.PIPE, 
                           stdout=sys.stdout
                       )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 2: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)
         
                    except Exception as e:
                        print(f'receiving exception when running step 2: {str(e)}')
                        exit(-1)
                       
                # step 3: generate traceroute graph json on IP and IP link
                if os.path.exists(graph_node_path):
                    print(f'completed step 3.1, generating node(ip address)-based graph data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 3.1: generating node(ip address)-based graph data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_node_path
                            ],
                            check=True, 
                            text=True, 
                            stderr=subprocess.PIPE, 
                            stdout=sys.stdout
                        )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 3.1: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)
         
                    except Exception as e:
                        print(f'receiving exception when running step 3.1: {str(e)}')
                        exit(-1)

                if os.path.exists(graph_edge_path):
                    print(f'completed step 3.2, creating edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 3.2, create edge(path link pair)-based graph data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_edge_path,
                            '--target', 'edge',
                            ],
                            check=True,
                            text=True,
                            stderr=subprocess.PIPE,
                            stdout=sys.stdout,
                            )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 3.2: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)

                    except Exception as e:
                        print(f'receiving exception when running step 3.2: {str(e)}')
                        exit(-1)
                
                # step 4: generate graph visuals
                if os.path.exists(graph_vis_dir):
                    print(f'completed step 4, generating graph visual data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 4: generating graph visual data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_tracegraph',
                            '--in_path', probe_filter_path,
                            '--out_dir', graph_vis_dir,
                            '--out_format', 'xml'
                            ],
                            check=True, 
                            text=True, 
                            stderr=subprocess.PIPE, 
                            stdout=sys.stdout
                    )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 4: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)
         
                    except Exception as e:
                        print(f'receiving exception when running step 4: {str(e)}')
                        exit(-1)

                # step 5: generate traceroute graph on cross-cn link
                if os.path.exists(graph_crosscn_path):
                    print(f'completed step 5, generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}. skipping...')
                else:
                    print(f'step 5: generating cross-cn edge(path link pair)-based graph data from {vp} to {dst}.')
                    try:
                        subprocess.run([
                            'python', '-m', 'proc.gen_crosscn',
                            '--in_path', probe_filter_path,
                            '--out_path', graph_crosscn_path,
                            ],
                            check=True,
                            text=True,
                            stderr=subprocess.PIPE,
                            stdout=sys.stdout
                            )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 5: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)

                    except Exception as e:
                        print(f'receiving exception when running step 5: {str(e)}')
                        exit(-1)
     
                # step 6: generate asn distribution data for specified dst cns
                if os.path.exists(asndist_path):
                    print(f'completed step 6, generating asn distribution data from {vp} to {avail_dst}. skipping...')
                else:
                    print(f'step 6: generating asn distribution data from {vp} to {dst}')
                    try:
                        result = subprocess.run([
                            'python', '-m', 'proc.gen_asndist',
                            '--in_path', probe_filter_path,
                            '--out_path', asndist_path,
                            ],
                            check=True, 
                            text=True, 
                            stderr=subprocess.PIPE, 
                            stdout=sys.stdout
                        )

                    except subprocess.CalledProcessError as e:
                        print(f'error running step 6: the script exited with a non-zero status code {e.returncode}')
                        print(f'stderr: {e.stderr}')
                        exit(-1)

                    except Exception as e:
                        print(f'receiving exception when running step 6: {str(e)}')
                        exit(-1)
