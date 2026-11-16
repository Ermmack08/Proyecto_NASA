# Funciones para construir mapas interactivos con Folium.
# Las vistas ráster ligeras se preparan previamente; no se cargan escenas originales
# ni se realiza procesamiento geoespacial durante las interacciones.

import folium
from streamlit_folium import st_folium
from config import MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM
from modules.i18n import translate as t

def build_base_map(boundary=None, zones=None, raster_layers=None, selected_point=None):
    """Crea mapa base y añade las geometrías disponibles."""
    map_object = folium.Map(
        location=MAP_DEFAULT_CENTER,
        zoom_start=MAP_DEFAULT_ZOOM,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for layer in raster_layers or []:
        folium.raster_layers.ImageOverlay(
            image=layer["image"],
            bounds=layer["bounds"],
            name=layer["name"],
            opacity=layer.get("opacity", 0.8),
            interactive=False,
            cross_origin=False,
            zindex=1,
            show=layer.get("show", False),
        ).add_to(map_object)

    if boundary and boundary.get("features"):
        first_properties = boundary["features"][0].get("properties", {})
        tooltip_fields = [
            (field, alias)
            for field, alias in (
                ("MpNombre", t("municipality")),
                ("Depto", t("department")),
                ("MpCodigo", t("dane_code")),
            )
            if field in first_properties
        ]
        boundary_layer = folium.GeoJson(
            boundary,
            name=t("map_base_layer"),
            style_function=lambda _: {
                "color": "#245c35", "weight": 3, "fillOpacity": 0.05
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[field for field, _ in tooltip_fields],
                aliases=[alias for _, alias in tooltip_fields],
            ) if tooltip_fields else t("map_base_layer"),
        ).add_to(map_object)
        map_object.fit_bounds(boundary_layer.get_bounds(), padding=(20, 20))

    if zones and zones.get("features"):
        features = zones["features"]
        has_zone_names = all(
            "name" in feature.get("properties", {})
            for feature in features
        )
        folium.GeoJson(
            zones,
            name=t("map_zones_layer"),
            style_function=lambda _: {
                "color": "#b45309", "weight": 2, "fillOpacity": 0.18
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name"] if has_zone_names else [],
                aliases=[t("zone")],
            ) if has_zone_names else None,
        ).add_to(map_object)

    if selected_point:
        folium.CircleMarker(
            location=[
                selected_point["latitude"],
                selected_point["longitude"],
            ],
            radius=7,
            color="#d9480f",
            weight=2,
            fill=True,
            fill_color="#ff922b",
            fill_opacity=0.9,
            tooltip=t("map_point"),
        ).add_to(map_object)

    folium.LayerControl(collapsed=False).add_to(map_object)
    return map_object

def render_map(map_object, height=580, key="agroadapt_map"):
    """Renderiza Folium en Streamlit y devuelve la interacción del usuario."""
    return st_folium(map_object, height=height, width=None, key=key)
