# Página 1: mapa territorial.
# El integrante GIS debe entregar el límite municipal y, si existen, las zonas de análisis
# en formato GeoJSON (coordenadas en WGS84 / EPSG:4326).

import math

import streamlit as st
from config import PROCESSED_DIR, SATELLITE_RASTER_FILES
from modules.data_loader import (
    load_boundary,
    load_satellite_metadata,
    sample_satellite_point,
    load_zones,
)
from modules.map_utils import build_base_map, render_map
from modules.i18n import translate as t

st.title(t("territory_title"))
st.caption(t("territory_caption"))

boundary = load_boundary()
zones = load_zones()
satellite_metadata = load_satellite_metadata()
satellite_products = (
    satellite_metadata.get("products", {}) if satellite_metadata else {}
)
satellite_layers = []
product_labels = {
    "sentinel2_ndvi": t("layer_ndvi"),
    "sentinel2_rgb": t("layer_rgb"),
    "nasadem_elevation": t("layer_elevation"),
    "nasadem_slope": t("layer_slope"),
}
available_products = {
    key: satellite_products[key]
    for key in product_labels
    if key in satellite_products
    and (PROCESSED_DIR / satellite_products[key].get("preview_file", "")).is_file()
    and SATELLITE_RASTER_FILES[key].is_file()
}
selected_product_key = None
selected_product = None

if available_products:
    selected_product_key = st.selectbox(
        t("layer_to_query"),
        options=list(available_products),
        format_func=lambda key: product_labels[key],
        key="territory_raster_filter",
        help=t("query_same_layer"),
    )
    selected_product = available_products[selected_product_key]
    preview_path = PROCESSED_DIR / selected_product["preview_file"]
    raster_layer_name = (
        f"{product_labels[selected_product_key]} · "
        f"{selected_product.get('acquisition_date', '')}"
    ).strip(" ·")
    satellite_layers = [
        {
            "image": str(preview_path),
            "bounds": selected_product["bounds"],
            "name": raster_layer_name,
            "opacity": 0.82 if selected_product_key == "sentinel2_ndvi" else 0.9,
            "show": True,
        }
    ]

if boundary is None or not boundary.get("features"):
    st.warning(t("missing_boundary"))
else:
    properties = boundary["features"][0].get("properties", {})
    municipality = properties.get("MpNombre", "Ebéjico")
    department = properties.get("Depto", "Antioquia")
    code = properties.get("MpCodigo", "05240")
    st.caption(
        t(
            "municipal_boundary",
            municipality=municipality,
            department=department,
            code=code,
        )
    )
    st.info(t("boundary_warning"))
if zones is None or not zones.get("features"):
    st.info(t("no_zones"))

if satellite_metadata and not satellite_layers:
    st.warning(t("missing_previews"))
elif not satellite_metadata:
    st.info(t("satellite_not_ready"))
else:
    if (
        "nasadem_elevation" in satellite_products
        and "nasadem_slope" not in satellite_products
    ):
        st.info(
            t("slope_not_ready")
        )
    sentinel = satellite_products.get("sentinel2_ndvi", {})
    nasadem = satellite_products.get("nasadem_elevation", {})
    slope = satellite_products.get("nasadem_slope", {})
    metric_columns = st.columns(5)
    metric_columns[0].metric(
        t("sentinel_scene"),
        sentinel.get("acquisition_date", "—"),
    )
    mean_ndvi = sentinel.get("mean_ndvi")
    metric_columns[1].metric(
        t("municipal_mean_ndvi"),
        f"{mean_ndvi:.2f}" if isinstance(mean_ndvi, (int, float)) else "—",
    )
    valid_coverage = sentinel.get("valid_coverage_percent")
    metric_columns[2].metric(
        t("clear_area"),
        f"{valid_coverage:.1f}%" if isinstance(valid_coverage, (int, float)) else "—",
    )
    minimum_elevation = nasadem.get("elevation_min_m")
    maximum_elevation = nasadem.get("elevation_max_m")
    elevation_range = (
        f"{minimum_elevation:.0f}–{maximum_elevation:.0f} m"
        if isinstance(minimum_elevation, (int, float))
        and isinstance(maximum_elevation, (int, float))
        else "—"
    )
    metric_columns[3].metric(t("elevation"), elevation_range)
    mean_slope = slope.get("slope_mean_degrees")
    metric_columns[4].metric(
        t("mean_slope"),
        f"{mean_slope:.1f}°" if isinstance(mean_slope, (int, float)) else "—",
    )

map_object = build_base_map(
    boundary=boundary,
    zones=zones,
    raster_layers=satellite_layers,
    selected_point=st.session_state.get("territory_selected_point"),
)
map_result = render_map(map_object)
map_click = map_result.get("last_clicked") if isinstance(map_result, dict) else None

if isinstance(map_click, dict):
    try:
        clicked_point = {
            "latitude": float(map_click["lat"]),
            "longitude": float(map_click["lng"]),
        }
    except (KeyError, TypeError, ValueError):
        clicked_point = None
    if clicked_point and all(math.isfinite(value) for value in clicked_point.values()):
        previous_point = st.session_state.get("territory_selected_point")
        point_changed = not isinstance(previous_point, dict) or any(
            key not in previous_point
            or not math.isclose(
                previous_point[key],
                clicked_point[key],
                rel_tol=0,
                abs_tol=1e-8,
            )
            for key in ("latitude", "longitude")
        )
        if point_changed:
            st.session_state["territory_selected_point"] = clicked_point
            st.rerun()

selected_point = st.session_state.get("territory_selected_point")
st.subheader(t("point_information"))
if selected_point and selected_product_key:
    st.caption(
        t(
            "selected_point",
            latitude=selected_point["latitude"],
            longitude=selected_point["longitude"],
            layer=product_labels[selected_product_key],
        )
    )
    product_details = []
    acquisition_date = selected_product.get("acquisition_date")
    if acquisition_date:
        product_details.append(t("scene_date", date=acquisition_date))
    resolution_m = selected_product.get(
        "resolution_m", selected_product.get("resolution_m_approx")
    )
    if isinstance(resolution_m, (int, float)):
        product_details.append(t("approx_resolution", resolution=resolution_m))
    if selected_product.get("source"):
        product_details.append(selected_product["source"])
    if product_details:
        st.caption(" · ".join(product_details))

    point_data = sample_satellite_point(
        selected_product_key,
        selected_point["latitude"],
        selected_point["longitude"],
    )
    if point_data is None:
        st.warning(t("no_pixel_value"))
    else:
        pixel_center = point_data["pixel_center"]
        st.caption(
            t(
                "pixel_center",
                latitude=pixel_center["latitude"],
                longitude=pixel_center["longitude"],
            )
        )
        if selected_product_key == "sentinel2_ndvi":
            st.metric(t("point_ndvi"), f"{point_data['values'][0]:.3f}")
            st.caption(t("ndvi_note"))
        elif selected_product_key == "sentinel2_rgb":
            reflectance = [value * 0.0001 for value in point_data["values"]]
            band_columns = st.columns(3)
            for column, label, value in zip(
                band_columns,
                (t("red_band"), t("green_band"), t("blue_band")),
                reflectance,
            ):
                column.metric(label, f"{value:.3f}")
            st.caption(t("rgb_reflectance"))
        elif selected_product_key == "nasadem_elevation":
            st.metric(t("point_elevation"), f"{point_data['values'][0]:.0f} m")
        else:
            st.metric(t("point_slope"), f"{point_data['values'][0]:.1f}°")
            st.caption(t("slope_note"))
else:
    st.info(t("click_map"))

if satellite_metadata:
    st.markdown(t("map_reading"))
    st.caption(t("terrain_note"))

with st.expander(t("integration_info")):
    st.markdown(t("layer_integration_markdown"))
