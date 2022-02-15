import streamlit as st


def remove_top_padding():

    st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            padding: {1}rem {1}rem {1}rem;
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )

    # removing the footer
    hide_streamlit_style = """
            <style>
            .css-8xv65a {display: None;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def remove_sidebar_padding():

    # css-17eq0hr e1fqkh3o1
    st.markdown(
             """
            <style>
            [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
                padding: 0rem;
            }
            [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
                padding: 0rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
