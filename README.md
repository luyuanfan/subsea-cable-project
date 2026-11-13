## File structure
```plaintext
-> prepare_metadata_pipeline.py 

-> configs/
   -> global_constants.py [static paths shared by all components, do not edit]
   -> validate_project_config.py
   -> example_project/
      -> example_config.py

-> data/ [git ignored]

-> images/ [git ignored]

-> vis/
   -> __init__.py
   -> preliminary_visual.py
   -> route_presence_visual.py
   -> hop_graph_visual.py
   -> crosscn_asn_visual.py

-> proc/
   -> __init__.py
   -> geodata_filter.py
   -> traceroute_graph.py
   -> aggre_crosscn_data.py
   -> explore_destinations.py
   -> traceroute_crosscn.py

-> terminal/
   -> ip_checker.py

-> remote/ [responsible for processing raw data on ssh remote server]
   -> aggregate_itdk_jsonl.py
   -> aggregate_raw_measurement.py
   -> parser.py
   -> errors.py
   -> utils.py

-> clas
   -> bootstrap_cusum.py
   -> cusum.py
   -> ewma.py
   -> glr_cusum.py

-> web/ [streamlit visualization app]

-> requirements.txt
```

## Setup

```bash
sudo add-apt-repository ppa:matthewluckie/scamper
sudo apt-get install scamper python3-scamper scamper-utils scamper-remoted scamper-hoiho libscamperfile13 libscamperfile13-dev libscamperctrl4 libscamperctrl4-dev
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Config

Every step of the pipeline (data extraction, preparation, and visualization) uses
a single project config file passed via `--config`. Create one per incident of
interest, e.g. `configs/redsea/config.py` (see `configs/example_project/example_config.py`):

```python
import os

# directory structure: raw ARK data goes in BUFFER_DIR, computed stats in STATS_DIR
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
BUFFER_DIR = f"{PROJECT_DIR}/buffer"
STATS_DIR = f"{PROJECT_DIR}/stats"

# vantage points of interest. "country" is required; "airport" and "probe_id"
# are optional refinements.
# refer to the table and map of ARK node locations:
# https://www.caida.org/projects/ark/locations/
VP_LIST = [
    {"country": "ke"},
    {"country": "za"},
    {"country": "gh"},
    {"country": "fr", "airport": "cdg"},
    # {"country": "fr", "airport": "cdg", "probe_id": "1"},  # single VP in an airport
]

# start and end time (YYYYMM) of captures
START_TIME = "202401"
END_TIME = "202403"
```

## Extract Traceroute Data from Ark
> This part should be done on the superserver. All raw data should already be present
> or must be downloaded in advance. 

```bash
python3 remote/aggregate_raw_measurement.py --config [path to config .py]
```

This aggregates raw data for every entry in `VP_LIST` into `BUFFER_DIR`, one
subdirectory per vantage point (e.g. `ke/`, `fr-cdg/`).

## Prepare Data

Copy the extracted data into `BUFFER_DIR` if it is not already there, then run:

```bash
python3 prepare_metadata_pipeline.py --config [path to config .py]
```

The buffer directory remains unchanged, and the pre-computed statistics appear under
`STATS_DIR`:
```
-> stats/
   --> probe-filter/
   --> outputs/
   --> graphs/
   --> asn-dist/
   --> prelim/
```

## Visualize Data

The web app reads the same config file (stats location, vantage points, time range):

```bash
streamlit run web/starter.py -- --config [path to config .py]
```
*Note: if you are on a remote server, this requires the remote server to be listening from localhost port 8501. To ensure this add '-L 8501:localhost:8501' when connecting to ssh remote server*

## Database Dependencies
Download ['IPinfo Lite database'](https://ipinfo.io/dashboard/downloads) to `data/ipinfo_lite.mmdb`.
Download [ISO 3166 Countries with Regional Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv) to `data/iso-3166-countries-with-regional-codes.csv`. 
