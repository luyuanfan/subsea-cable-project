import streamlit as st
from utils.constants import STATS_ROOT_DIR, SRC2DST_JSON
from utils.time_processor import aggre_avail_data, filter_avail_data
import os, re
from .reusable_comp import savefig_button

def render_heatmap_realtime(select_src, select_dst, select_start, select_end, processor=None):
    if not select_src or not select_dst or not processor or not select_start or not select_end:
        return
    vp = select_src.split('|')[1]
    dst = select_dst.split('|')[1]
    json_dir = f'{STATS_ROOT_DIR}/{SRC2DST_JSON}'
    select_type = st.segmented_control("IP spec", ('IP Address', 'IP Link', 'Cross-country IP Link'), selection_mode='single')
    select_spec = st.segmented_control("heatmap type", ("Presence", "Density"), selection_mode='single')
    if not select_type or not select_spec:
        return
    suffix = f'{vp}2{dst}'
    if select_type == 'Cross-country IP Link':
        suffix += '_crosscn_edge'
    elif select_type == 'IP Link':
        suffix += '_edge'
    else:
        suffix += '_node'

    suffix += '.json'
    data, asn_choices = aggre_avail_data(json_dir, suffix, select_start, select_end)

    if len(data) == 0:
        st.write(f'unable to find data for {select_type}, {select_spec} for {vp}2{dst} in {json_dir}')
    else:
        select_asns = st.segmented_control('major AS names', asn_choices, selection_mode='multi')
        data = filter_avail_data(data, select_asns)
        start_time = select_start.strftime('%y-%m-%d')
        end_time = select_end.strftime('%y-%m-%d')
        fig1, _ = processor(data, start_time, end_time, mode=select_spec.lower())

        start_str = select_start.strftime('%m%d')
        end_str = select_end.strftime('%m%d')
        type_str = '_'.join(select_type.lower().split())
        spec_str = select_spec.lower()
        img_path = f'vis_heatmap_{vp}2{dst}_{start_str}_{end_str}_{type_str}_{spec_str}'
        if len(select_asns) > 0:
            asn_sample = select_asns[0]
            asn_sample = '_'.join(asn_sample.lower().split())
            asn_sample = re.sub(r'[/,]', r'', asn_sample)
            img_path += f'_{asn_sample}'
            if len(select_asns) > 1:
                img_path += f'(et{len(select_asns)-1})'

        img_path += '.png'
        savefig_button(fig1, 'images', img_path)
        st.pyplot(fig1)
 
