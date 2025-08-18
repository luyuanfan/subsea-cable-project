import streamlit as st
import os, json
from utils.constants import STATS_ROOT_DIR, SRC_ASNDIST
from utils.time_processor import aggre_avail_data
from .reusable_comp import savefig_button

def render_crosscn_asn_realtime(select_src, select_dst, select_start, select_end, 
                                processor=None):
    if not select_src or not select_dst or not select_start or not select_end or not processor:
        return

    vp = select_src.split('|')[1]
    dst = select_dst.split('|')[1]
    asndist_dir = f'{STATS_ROOT_DIR}/{SRC_ASNDIST}'
    suffix = f'{vp}2{dst}.json' 
    start_str = select_start.strftime('%m%d')
    end_str = select_end.strftime('%m%d')
    data, asn_list = aggre_avail_data(asndist_dir, suffix, select_start, select_end, data_type='dict dict')
    if len(data) == 0:
        st.write(f'no preliminary data available from {vp} to {dst}.')
        return
    
    img_path = f'crosscn_asndist_{vp}2{dst}_{start_str}_{end_str}'
    fig = processor(data, asn_list)
    savefig_button(fig, 'images', img_path)
    st.pyplot(fig)
        

