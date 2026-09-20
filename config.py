import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = f"{ROOT_DIR}/data"
PROC_DIR = f"{ROOT_DIR}/proc"

ARK_BUF_DIR = f"{DATA_DIR}/test-buffer"
STATS_DIR = f"{DATA_DIR}/test-stats"

ARK_DIR = "/data/topology/ark/data/team-probing/list-7.allpref24/team-1/daily/2024"

ISO_FPATH = f"{DATA_DIR}/iso-3166-countries-with-regional-codes.csv"

START_TIME = "202401"
END_TIME = "202412"