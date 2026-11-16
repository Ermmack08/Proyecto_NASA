"""AgroAdapt Ebéjico Streamlit entry point."""

import streamlit as st

from config import APP_NAME, BASE_DIR, COLORS, LOGO_FILE
from modules.data_loader import load_environment
from modules.i18n import detect_system_language, translate as t
from modules.indicators import summarize_environment

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "agroadapt_language_mode" not in st.session_state:
    st.session_state["agroadapt_language_mode"] = "auto"
detected_language = detect_system_language()
language_mode = st.session_state["agroadapt_language_mode"]
control_language = detected_language if language_mode == "auto" else language_mode
language_mode = st.sidebar.selectbox(
    t("language_label", control_language),
    options=("auto", "es", "en"),
    format_func=lambda option: t(
        {
            "auto": "language_auto",
            "es": "language_spanish",
            "en": "language_english",
        }[option],
        control_language,
    ),
    key="agroadapt_language_mode",
)
st.session_state["agroadapt_language"] = (
    detected_language if language_mode == "auto" else language_mode
)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #E8F0E8 !important; }}
    .main-title {{
        color: {COLORS["primary"]};
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }}
    .main-description {{
        color: {COLORS["muted"]};
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }}
    .project-note {{
        background-color: {COLORS["light_green"]};
        border-left: 5px solid {COLORS["secondary"]};
        padding: 18px;
        border-radius: 8px;
        color: {COLORS["dark"]};
        margin-bottom: 25px;
    }}
    h2, h3 {{ color: {COLORS["primary"]}; }}
    div[data-testid="stMetric"] {{
        background-color: {COLORS["white"]};
        border: 1px solid {COLORS["border"]};
        padding: 18px;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_home() -> None:
    environment = load_environment()
    summary = summarize_environment(environment)

    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if LOGO_FILE.exists():
            st.image(str(LOGO_FILE), width=130)
    with col_title:
        st.markdown(
            f'<div class="main-title">{APP_NAME}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="main-description">{t("app_description")}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        f"""
        <div class="project-note">
            <b>{t("purpose_title")}</b><br><br>
            {t("purpose_text")}
            <br><br>
            {t("recommendation_validation")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(t("overview"))
    col1, col2, col3 = st.columns(3)
    col1.metric(t("environment_records"), summary["records"])
    col2.metric(t("available_variables"), summary["variables"])
    col3.metric(
        t("data_status"),
        t("demo") if summary["is_demo"] else t("data_loaded"),
    )

    st.divider()
    st.subheader(t("explore_agroadapt"))
    st.write(t("home_modules_intro"))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {t('nav_territory')}")
        st.write(t("territory_description"))
        st.markdown(f"### {t('nav_environment')}")
        st.write(t("environment_description"))
    with col2:
        st.markdown(f"### {t('nav_crops')}")
        st.write(t("crops_description"))
        st.markdown(f"### {t('nav_rotations')}")
        st.write(t("rotations_description"))

    st.divider()
    if summary["is_demo"]:
        st.warning(t("demo_data_warning"))
    else:
        st.info(t("loaded_data_info"))
    st.markdown(
        f"""
        <div style="
            text-align: center;
            color: {COLORS["muted"]};
            padding: 20px 0px;
            font-size: 0.85rem;
        ">{t("footer")}</div>
        """,
        unsafe_allow_html=True,
    )


navigation = st.navigation(
    [
        st.Page(
            render_home,
            title=t("nav_home"),
            icon="🌱",
            default=True,
        ),
        st.Page(
            str(BASE_DIR / "pages" / "1_Territorio.py"),
            title=t("nav_territory"),
            icon="🗺️",
        ),
        st.Page(
            str(BASE_DIR / "pages" / "2_Ambiente.py"),
            title=t("nav_environment"),
            icon="🌦️",
        ),
        st.Page(
            str(BASE_DIR / "pages" / "3_Cultivos.py"),
            title=t("nav_crops"),
            icon="🌱",
        ),
        st.Page(
            str(BASE_DIR / "pages" / "4_Rotaciones.py"),
            title=t("nav_rotations"),
            icon="🔄",
        ),
    ]
)
navigation.run()
