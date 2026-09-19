## File structure
```plaintext
-> prepare_metadata_pipeline.py 

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

## Extract Traceroute Data from Ark

> This part should be done on the superserver. 

Here is a **table** and **map** of [Ark node locations and names](https://www.caida.org/projects/ark/locations/).

To obtain data from all vantage points from a certain country, run:
```bash
python3 remote/aggregate_raw_measurement.py --country \[country iso code\]
```

The script also supports additional specifications on airport (via *--airport*) and identifiers (via *--probe_id*, use '-1' to default to the vp with no identifier).

An airport may have multiple vantage points (VP), with each VP having its own identifier.
To extract data from a specific VP in a given airport, do:
```bash
python3 remote/aggregate_raw_measurement.py --country fr --airport cdg --probe_id 1
python3 remote/aggregate_raw_measurement.py --country fr --airport cdg --probe_id 3
```

You can also extract data from all available VPs in the given airport by not specifying any VP identifier, such as:
```bash
python3 remote/aggregate_raw_measurement.py --country fr --airport cdg
```

If not airport and probe num is specified, the data extraction script will aggregate on all available vantage points from that country. 

## Prepare Data

For a specific incident of interest, put all aggregated vp of interest in the same folder and run: 
```bash
python3 prepare_metadata_pipeline.py --root_dir \[the root directory for data\] --data_dir \[directory name for raw data\]  --stats_dir \[directory used to place all outputs stats files\]
```

For example, to study the massive red sea outage, we would want vantage points *ke, za, gh, cdg-fr*. We will format the data directory as:
```
-> data/
   -> example-buf/
      -> ke/
      -> za/
      -> gh/
      -> cdg-fr/
```

Then to obtain all pre-computed statistical data, run:
```bash
python3 prepare_metadata_pipeline.py --root_dir data --data_dir example-buf  --stats_dir redsea-stats
```

After the scripts completes, the buf directory will remain unchanged and you will see additional directories now inside the stats_dir:
```
-> data/
   -> buf/ [unchanged]
      -> ke/
      -> za/
      -> gh/
      -> cdg-fr/

   -> redsea-stats/
      --> probe-filter/
      --> outputs/
      --> graphs/
      --> asn-dist/
      --> prelim/
```
These new statistics data can be used to further processing or visualizations. 

## Visualize Data
The current approach for data analytics and visualization uses Streamlit library. 

To tell the system where the statistics data are stored, modify the path information in **web/utils/constants.py*. Specifically, do
```plaintext
ROOT_DIR = [change to the directory specified when in preparation step's 'root_dir' argument]
CATEGORY = [change to the directory specified when in preparation step's 'stats_dir' argument]
```

Also, to specify which vantage points of interest, add **cn_specs.txt** inside the stats_dir. It will be a txt file where each line contains a vp of interest. For the redsea example, the txt file would look like:
```plaintext
ke
za
gh
cdg-fr
```

To start the port, run: 
```bash
streamlit run web/starter.py
```
*Note: if you are on a remote server, this requires the remote server to be listening from localhost port 8501. To ensure this add '-L 8501:localhost:8501' when connecting to ssh remote server*

## Database Dependencies
Download ['IPinfo Lite database'](https://ipinfo.io/dashboard/downloads) to `data/ipinfo_lite.mmdb`.
Download [ISO 3166 Countries with Regional Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv) to `data/iso-3166-countries-with-regional-codes.csv`. 


