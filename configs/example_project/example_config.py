import os

# Specify directory structure and file names
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
BUFFER_DIR = f"{PROJECT_DIR}/buffer"
STATS_DIR = f"{PROJECT_DIR}/stats"

# Specify from which viewpoints to download raw data, they will
# be placed in BUFFER_DIR
VP_LIST = [
    {
        "country"  : "fr",
        "airport"  : "cdg",
        "probe_id" : "1", 
    },
    {
        "country" : "ke",
    },
    {
        "country" : "za", 
    }
]

# Specify the start and end time (YYYYMM) of captures
START_TIME = "202401"
END_TIME = "202403"