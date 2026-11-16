"""Explore rotation scenarios provided by the agricultural modeling team."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.rotation_model import DEFAULT_WEIGHTS, compare_rotations
from modules.i18n import translate as t

st.title(t("rotations_title"))
st.caption(t("rotations_caption"))
st.info(t("rotations_upload_info"))

uploaded_file = st.file_uploader(t("scenario_file"), type=["json"])
if uploaded_file is None:
    st.stop()

try:
    rotations = json.loads(uploaded_file.getvalue().decode("utf-8"))
except (UnicodeDecodeError, json.JSONDecodeError) as error:
    st.error(t("json_read_error", error=error))
    st.stop()

st.subheader(t("comparison_weights"))
st.caption(t("weights_caption"))
weights = {}
columns = st.columns(len(DEFAULT_WEIGHTS))
for column, (criterion, default_weight) in zip(columns, DEFAULT_WEIGHTS.items()):
    with column:
        weights[criterion] = st.slider(
            t(criterion),
            min_value=0,
            max_value=100,
            value=int(default_weight * 100),
            step=5,
            key=f"rotation_weight_{criterion}",
        )

try:
    results = compare_rotations(rotations, weights=weights)
except ValueError as error:
    st.error(t("invalid_scenario_file", error=error))
    st.stop()

table = pd.DataFrame(
    [
        {
            t("scenario"): result["name"],
            t("exploratory_index"): result["score"],
            t("description"): result["description"],
        }
        for result in results
    ]
)

st.subheader(t("comparison"))
st.dataframe(table, use_container_width=True, hide_index=True)

chart = px.bar(
    table,
    x=t("scenario"),
    y=t("exploratory_index"),
    range_y=[0, 100],
    title=t("weighted_chart_title"),
)
st.plotly_chart(chart, use_container_width=True)

for result in results:
    with st.expander(result["name"]):
        st.write(result["description"])
        st.write(f"**{t('received_scores')}**")
        st.json(
            {
                t(criterion): score
                for criterion, score in result["scores"].items()
            }
        )
        st.write(f"**{t('limitations_assumptions')}**")
        st.warning(result["limitations"])

st.warning(t("rotation_warning"))
