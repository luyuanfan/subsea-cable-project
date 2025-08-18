import streamlit as st
from utils.constants import STATS_ROOT_DIR, CN_SPEC
from utils.utils import reset_page
import os, datetime

def render_primary_realtime():
    with open(f'{STATS_ROOT_DIR}/{CN_SPEC}', 'r') as f:
        dirs = f.read().split('\n')
    dirs = sorted(dirs)
    isos = [dir_item.split('-')[0] for dir_item in dirs]
    iso_specs = ['-'.join(dir_item.split('-')[1:]) if len(dir_item.split('-')) > 1 else '' for dir_item in dirs]
    src_names = [f"{st.session_state.iso2cn[iso]}[{iso_spec}]|{dir_item}" for iso, iso_spec, dir_item in zip(isos, iso_specs, dirs) if st.session_state.iso2cn.get(iso, None)]
    dst_names = [f"{st.session_state.iso2cn[iso]}|{iso}" for iso in list(set(isos)) if st.session_state.iso2cn.get(iso, None)]
    select_cat = st.selectbox(
            'statistics category',
            ('Preliminary data', 'Cross-Country ASNs', 'IP Utilization Heatmap', 'IP Hop Connectivity Graph', 'IP Traceroute Changes Classification Method'),
            index=None,
            placeholder='select a category of interest',
            on_change=reset_page)

    select_src, select_dst = None, None
    select_start, select_end = None, None
    if select_cat and len(src_names) > 0 and len(dst_names) > 0:
        select_src = st.selectbox(
                'vantage point', sorted(src_names), index=None,
                placeholder='select a vantage point', on_change=reset_page)
        select_dst = st.selectbox(
                'probe destination', sorted(dst_names), index=None,
                placeholder='select a destination', on_change=reset_page)
    
        if select_cat != 'IP Hop Connectivity Graph':
            select_start = st.date_input('statistics start time', datetime.date(2024, 11, 1))
            select_end = st.date_input('statistics end time', datetime.date(2024, 12, 31))

    return select_cat, select_src, select_dst, select_start, select_end
