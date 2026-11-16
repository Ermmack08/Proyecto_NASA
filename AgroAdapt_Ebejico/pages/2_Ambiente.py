# Página 2: variables ambientales y series temporales.
# El equipo de datos debe entregar una tabla procesada con fecha, variables, unidades y fuente.

import streamlit as st
import plotly.express as px
from modules.data_loader import load_environment
from modules.i18n import translate as t
from modules.indicators import monthly_summary

st.title(t("environment_title"))

VARIABLE_LABELS = {
    "temperature_c": (t("temperature"), "°C"),
    "precipitation_mm_day": (t("precipitation"), t("mm_per_day")),
    "relative_humidity_pct": (t("humidity"), "%"),
}

df = load_environment()
if df.empty:
    st.warning(
        t("no_environment")
    )
    st.stop()

if df["is_demo"].any():
    st.warning(t("synthetic_warning"))

st.caption(t("environment_caption"))

if df["source"].astype("string").str.contains("NASA POWER", case=False, na=False).any():
    st.warning(
        t("power_warning")
    )
    st.link_button(
        t("power_docs"),
        "https://power.larc.nasa.gov/docs/services/api/temporal/monthly/",
    )

numeric_cols = [
    column for column in df.select_dtypes(include="number").columns
    if column != "is_demo"
]
if not numeric_cols:
    st.info(t("no_numeric_environment"))
else:
    selected = st.selectbox(
        t("environment_variable"),
        numeric_cols,
        format_func=lambda column: VARIABLE_LABELS.get(column, (column, ""))[0],
    )
    variable_label, unit = VARIABLE_LABELS.get(selected, (selected, ""))
    chart_data = monthly_summary(df)
    if not chart_data.empty:
        fig = px.line(
            chart_data,
            x="month",
            y=selected,
            markers=True,
            title=t("monthly_series", variable=variable_label),
            labels={"month": t("month"), selected: f"{variable_label} ({unit})"},
        )
        st.plotly_chart(fig, use_container_width=True)
        average = f"{df[selected].mean():.2f} {unit}".strip()
        st.metric(t("average", variable=variable_label), average)

    st.caption(t("precipitation_note"))

st.subheader(t("data_provenance"))
date_start = df["date"].min().date()
date_end = df["date"].max().date()
st.caption(t("date_coverage", start=date_start, end=date_end))
sources = sorted(df["source"].dropna().astype(str).unique())
st.caption(t("declared_sources", sources=", ".join(sources) if sources else t("no_source")))
environment_column_labels = {
    "date": t("date_column"),
    "temperature_c": t("temperature"),
    "precipitation_mm_day": t("precipitation"),
    "relative_humidity_pct": t("humidity"),
    "source": t("source_column"),
    "is_demo": t("demo_column"),
}
st.dataframe(
    df.rename(columns=environment_column_labels),
    use_container_width=True,
)
st.info(t("environment_info"))
