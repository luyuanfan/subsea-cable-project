import streamlit as st
import os
from datetime import datetime
from .reusable_comp import render_button, savefig_button
from utils.constants import STATS_ROOT_DIR, SRC2DST_GRAPH, SRC2DST_JSON
from utils.utils import reset_page

def render_graphvis_realtime(select_src, select_dst, processor):
    if not select_src or not select_dst or not processor:
        return

    vp = select_src.split('|')[1]
    dst = select_dst.split('|')[1]
    img_dir = f'{STATS_ROOT_DIR}/{SRC2DST_GRAPH}'
    suffix = f'_{vp}2{dst}'
    graphs = []
    
    if os.path.exists(img_dir):
        for d in os.listdir(img_dir):

            if d.endswith(suffix):
                path = os.path.join(img_dir, d)
                graphs.extend([os.path.join(path, f) for f in os.listdir(path)])

    graphs = sorted(graphs)
    date2idx = {}
    min_day, max_day = None, None
    for idx, graph in enumerate(graphs):
        date_str = graph.split('/')[-1].split('.')[0]
        date_time = datetime.strptime(date_str, '%y-%m-%d').date()   
        date2idx[date_time] = idx
        if idx == 0:
            min_day = date_time
        elif idx == len(graphs) - 1:
            max_day = date_time
 
    if len(graphs) == 0:
        st.write(f'no graph data available for {vp}2{dst} at {img_dir}')
        return
    
    def change_date():
        st.session_state.img_idx = date2idx[st.session_state.curr_date]

    select_date = st.date_input('select date of interest', min_day, key='curr_date', on_change=change_date, min_value=min_day, max_value=max_day)
    select_graph = st.segmented_control("graph specs", ("node", "edge"), default='node', selection_mode='single')
    select_threshold = st.slider('threshold', min_value=0, max_value=100, value=0)

    date_str = select_date.strftime('%m%d')
    img_path = f'graphvis_{vp}2{dst}_{select_graph}_{date_str}.png'
    fig = processor(graphs[st.session_state.img_idx], select_graph, select_threshold)
    savefig_button(fig, 'images', img_path)
    st.pyplot(fig)
    render_button(len(graphs))
