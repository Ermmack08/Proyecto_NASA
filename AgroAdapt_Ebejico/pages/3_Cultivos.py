# Página 3: catálogo agrícola.
# Los cultivos deben confirmarse con EVA/UPRA, UMATA, productores u otras fuentes locales.
# Los campos agronómicos no deben rellenarse con valores supuestos.

import streamlit as st
import plotly.express as px

from modules.data_loader import load_crop_history, load_crops
from modules.i18n import translate as t

st.title(t("crops_title"))

catalog_tab, history_tab = st.tabs([t("crop_sheets"), t("municipal_history")])

crop_field_labels = {
    "crop": t("crop"),
    "family": t("field_family"),
    "cycle": t("field_cycle"),
    "water_requirement": t("field_water_requirement"),
    "root_depth": t("field_root_depth"),
    "soil_requirements": t("field_soil_requirements"),
    "nutritional_notes": t("field_nutritional_notes"),
    "rotation_notes": t("field_rotation_notes"),
    "source": t("field_source"),
}

with catalog_tab:
    crops = load_crops()
    if crops.empty:
        st.warning(t("empty_catalog"))
    else:
        search = st.text_input(t("search_crop"))
        filtered_crops = crops[
            crops["crop"].astype("string").str.contains(search, case=False, na=False)
        ]
        if filtered_crops.empty:
            st.info(t("no_crop_matches"))
        else:
            selected_crop = st.selectbox(
                t("select_crop"),
                sorted(filtered_crops["crop"].dropna().unique()),
            )
            record = filtered_crops[filtered_crops["crop"] == selected_crop].iloc[0]

            st.subheader(selected_crop)
            if str(record.get("source", "")).strip().lower() in {
                "",
                "por verificar",
                "nan",
            }:
                st.warning(t("unverified_crop_source"))

            left, right = st.columns(2)
            with left:
                for field in ["family", "cycle", "water_requirement", "root_depth"]:
                    if field in record.index:
                        st.write(f"**{crop_field_labels.get(field, field)}:** {record[field]}")
            with right:
                for field in [
                    "soil_requirements",
                    "nutritional_notes",
                    "rotation_notes",
                    "source",
                ]:
                    if field in record.index:
                        st.write(f"**{crop_field_labels.get(field, field)}:** {record[field]}")

            st.caption(t("crop_sheet_note"))
            st.dataframe(
                filtered_crops.rename(columns=crop_field_labels),
                use_container_width=True,
                hide_index=True,
            )

with history_tab:
    history = load_crop_history()
    if history.empty:
        st.warning(t("empty_history"))
    else:
        first_year = int(history["year"].min())
        last_year = int(history["year"].max())
        crop_count = int(history["crop"].nunique())

        metric_columns = st.columns(3)
        metric_columns[0].metric(t("published_records"), len(history))
        metric_columns[1].metric(t("reported_crops"), crop_count)
        metric_columns[2].metric(t("recorded_coverage"), f"{first_year}–{last_year}")

        st.caption(t("eva_source_caption"))
        st.link_button(
            t("original_dataset"),
            "https://www.datos.gov.co/d/2pnw-mmge",
        )

        st.warning(t("eva_warning"))

        selected_crop = st.selectbox(
            t("history_crop"),
            sorted(history["crop"].unique()),
            key="history_crop",
        )
        selected_history = history[history["crop"] == selected_crop].copy()

        metric_labels = {
            "area_planted_ha": t("planted_area"),
            "area_harvested_ha": t("harvested_area"),
            "production_t": t("production"),
            "yield_t_ha": t("yield"),
        }
        selected_metric = st.selectbox(
            t("indicator"),
            list(metric_labels),
            format_func=metric_labels.__getitem__,
        )
        chart = px.scatter(
            selected_history,
            x="year",
            y=selected_metric,
            color="crop_detail",
            hover_data=[
                "crop_group",
                "crop_subgroup",
                "scientific_name",
                "crop_cycle",
                "area_planted_ha",
                "area_harvested_ha",
                "production_t",
                "yield_t_ha",
            ],
            labels={
                "year": t("year"),
                selected_metric: metric_labels[selected_metric],
                "crop_detail": t("reported_detail"),
                "crop_group": t("crop_group"),
                "crop_subgroup": t("crop_subgroup"),
                "scientific_name": t("scientific_name"),
                "crop_cycle": t("eva_cycle"),
                "area_planted_ha": t("planted_area"),
                "area_harvested_ha": t("harvested_area"),
                "production_t": t("production"),
                "yield_t_ha": t("yield"),
            },
            title=t(
                "reported_value",
                metric=metric_labels[selected_metric],
                crop=selected_crop.title(),
            ),
        )
        chart.update_xaxes(dtick=1)
        st.plotly_chart(chart, use_container_width=True)

        display_columns = {
            "year": t("year"),
            "crop": t("crop"),
            "crop_detail": t("reported_detail"),
            "crop_cycle": t("eva_cycle"),
            "area_planted_ha": t("planted_area"),
            "area_harvested_ha": t("harvested_area"),
            "production_t": t("production"),
            "yield_t_ha": t("yield"),
        }
        st.dataframe(
            selected_history[list(display_columns)].rename(columns=display_columns),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            t("download_crop_records"),
            data=selected_history.to_csv(index=False).encode("utf-8-sig"),
            file_name="historico_eva_ebejico.csv",
            mime="text/csv",
        )
