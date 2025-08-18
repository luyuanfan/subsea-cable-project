import streamlit as st
from utils.constants import STATS_ROOT_DIR, SRC2DST_PRELIM
from utils.time_processor import aggre_avail_data, filter_avail_data
from .reusable_comp import render_button, savefig_button
import os, re

def render_prelim_realtime(select_src, select_dst, select_start, select_end, 
    processor=None):
    if not select_src or not select_dst or not processor:
        return
    vp = select_src.split('|')[1]
    dst = select_dst.split('|')[1]
    prelim_dir = f'{STATS_ROOT_DIR}/{SRC2DST_PRELIM}'
    suffix = f'{vp}2{dst}.json'
    data, asn_choices = aggre_avail_data(prelim_dir, suffix, select_start, select_end, data_type='list dict')
    if len(data) == 0:
        st.write(f'no preliminary data available from {vp} to {dst}.')
        return
    select_asns = st.segmented_control('major AS names', asn_choices, selection_mode='multi')
    data = filter_avail_data(data, select_asns, data_type='list')
    select_rtt_threshold = st.slider('rtt threshold', min_value=0, max_value=2000)
    select_hop_threshold = st.slider('hop count threshold', min_value=0, max_value=30)
    figs = processor(data, select_rtt_threshold, select_hop_threshold)
    start_str = select_start.strftime('%m%d')
    end_str = select_end.strftime('%m%d')
    img_path = f'prelim{st.session_state.img_idx}_{vp}2{dst}_{start_str}_{end_str}'
    if len(select_asns) > 0:
        asn_sample = select_asns[0]
        asn_sample = '_'.join(asn_sample.lower().split())
        asn_sample = re.sub(r'[/,]', r'', asn_sample)
        img_path += f'_{asn_sample}'
        if len(select_asns) > 1:
            img_path += f'(et{len(select_asns)-1})'
    img_path += '.png'
    savefig_button(figs[st.session_state.img_idx], 'images', img_path)
    st.pyplot(figs[st.session_state.img_idx])
    render_button(2) 


