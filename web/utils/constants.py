"""
Loads project config for web visualization.
"""
import os
import sys
import argparse

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs.global_constants import ISO_FPATH
from configs.validate_project_config import read_validate_config


def _parse_config_path():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    args, _ = parser.parse_known_args()
    return args.config


def _build_vp_name(vp):
    parts = [vp['country']]
    if vp.get('airport'):
        parts.append(vp['airport'])
    if vp.get('probe_id'):
        parts.append(str(vp['probe_id']))
    return '-'.join(parts)


_cfg = read_validate_config(_parse_config_path())

STATS_ROOT_DIR = _cfg.STATS_DIR
VP_NAMES = sorted(_build_vp_name(vp) for vp in _cfg.VP_LIST)
START_TIME = _cfg.START_TIME
END_TIME = _cfg.END_TIME

SRC2DST_RAW = 'probe-filter'
SRC2DST_JSON = 'outputs'
SRC2DST_GRAPH = 'graphs'
SRC2DST_PRELIM = 'prelim'
SRC_ASNDIST = 'asn-dist'