import streamlit as st
from utils.constants import VP_NAMES, START_TIME, END_TIME
from utils.utils import reset_page
import datetime, calendar

def ym_to_date(ym, last_day=False):
    year, month = int(ym[:4]), int(ym[4:6])
    day = calendar.monthrange(year, month)[1] if last_day else 1
    return datetime.date(year, month, day)

def render_primary_realtime():
    dirs = sorted(VP_NAMES)
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
            select_start = st.date_input('statistics start time', ym_to_date(START_TIME))
            select_end = st.date_input('statistics end time', ym_to_date(END_TIME, last_day=True))

    return select_cat, select_src, select_dst, select_start, select_end
