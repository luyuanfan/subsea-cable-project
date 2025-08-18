import streamlit as st
import os, sys, re
from utils.constants import STATS_ROOT_DIR, SRC2DST_JSON, SRC2DST_PRELIM
from .reusable_comp import savefig_button
from utils.time_processor import aggre_avail_data, filter_avail_data

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from clas.ewma import ewma_processor
from clas.cusum import cusum_processor
from clas.glr_cusum import glr_cusum_processor
from clas.bootstrap_cusum import bootstrap_cusum_processor

PROCESSOR_DICT = {
    'EWMA': ewma_processor,
    'CUSUM': cusum_processor,
    'GLR CUSUM': glr_cusum_processor,
    'bootstrap CUSUM': bootstrap_cusum_processor,
}
def render_clasout_realtime(select_src, select_dst, select_start, select_end):
    if not select_src or not select_dst or not select_start or not select_end:
        return
    vp = select_src.split('|')[1]
    dst = select_dst.split('|')[1]
    start_str = select_start.strftime('%m%d')
    end_str = select_end.strftime('%m%d')

    prelim_dir = f'{STATS_ROOT_DIR}/{SRC2DST_PRELIM}'
    suffix = f'{vp}2{dst}.json'
    data, asn_choices = aggre_avail_data(prelim_dir, suffix, select_start, select_end, data_type='list dict')
    if len(data) == 0:
        st.write(f'no preliminary data available from {vp} to {dst}.')
        return
    select_asns = st.segmented_control('major AS names', asn_choices, selection_mode='multi')
    data = filter_avail_data(data, select_asns, data_type='list')

    select_method = st.pills('select classification method', list(PROCESSOR_DICT.keys()))
    select_subject = st.pills('select the data to use', ('hop number', 'round-trip time'))

    if not select_method or not select_subject:
        return

    aggre = st.toggle('show aggregative statistics', value=True)
    disp_iplink = st.toggle('show ip link correspondence', value=False)
    iplink_data = None

    if disp_iplink:
        json_dir = f'{STATS_ROOT_DIR}/{SRC2DST_JSON}'
        iplink_suffix = f'{vp}2{dst}_crosscn_edge.json'
        iplink_data, _ = aggre_avail_data(json_dir, iplink_suffix, select_start, select_end)
        iplink_data = filter_avail_data(iplink_data, select_asns)
 
    select_spec = None
    if aggre:
        select_spec=st.segmented_control('select the statistics of interest', ('avg', 'med', 'max', 'min', 'q25', 'q75'), default='q25')
        if not select_spec:
            return

    ret_dates, fig = PROCESSOR_DICT[select_method](data, subject=select_subject, aggre=aggre, spec=select_spec, disp_iplink=disp_iplink, iplink_data=iplink_data)
    
    img_path = f'clas_{vp}2{dst}_{start_str}_{end_str}'
    img_path += f'_{"_".join(select_subject.lower().split())}'
    img_path += '_stats' if aggre else '_raw'
    img_path += f'_{select_spec}' if aggre else ''
    img_path += f'_{"_".join(select_method.lower().split())}'
    if len(select_asns) > 0:
        asn_sample = select_asns[0]
        asn_sample = '_'.join(asn_sample.lower().split())
        asn_sample = re.sub(r'[/,]', r'', asn_sample)
        img_path += f'_{asn_sample}'
        if len(select_asns) > 1:
            img_path += f'(et{len(select_asns)-1})'
    img_path += '.png'
    savefig_button(fig, 'images', img_path)
    st.pyplot(fig)
    date_str = ', '.join([d.strftime("%m-%d") for d in sorted(ret_dates)])
    st.write(f'algorithm classifies {len(ret_dates)} instances of level shifts, happening respectively on:')
    st.write(date_str)
