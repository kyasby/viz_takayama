import streamlit as st

sss = st.session_state

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from PIL import Image

from apps.utils import combine_df, load_date, set_params, upload_csv


# <span style='color: red;'></span>
def my_mkdwn(txt1, txt2, txt3=None):
    text = f"{txt1}  \n### {txt2}"
    if txt3:
        return text + f"\n #### {txt3}"
    else:
        return text


def app():
    params = set_params()
    pic_url, place_name, sss.df_day, hol_edge = load_date("day", params)

    st.title(f"{place_name}の分析の概要")
    st.write("このページは作成中なので，見た目しかありません。実際のデータとは連動していません。")
    a = 11340

    st.markdown("---")

    st.markdown("## 通行人数 ＊日〜火までの比較")
    col2, col3, col4 = st.columns([1, 1, 1])

    col2.markdown(my_mkdwn("**先週**", f"{a}人"))
    col3.markdown(my_mkdwn("**今週**", f"{a+1002}人"))
    col4.markdown(
        my_mkdwn("**先週と今週の比較**", f'<span style="color: green;">+100%</span>'),
        unsafe_allow_html=True,
    )

    char_data1 = pd.DataFrame(np.random.randn(7, 1), columns=["count"])
    char_data1["data"] = "先週"
    char_data2 = pd.DataFrame(np.random.randn(3, 1), columns=["count"])
    char_data2["data"] = "今週"

    df = pd.concat([char_data1, char_data2])

    fig = px.line(df, x=df.index, y="count", color="data", markers=True)

    config = {"staticPlot": True}
    st.image(fig)
    # st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("## 人が多い曜日")
    col2, col3, col4 = st.columns([1, 1, 1])

    col2.markdown(my_mkdwn("**1位**", f"土曜日", "30%"))
    col3.markdown(my_mkdwn("**2位**", f"日曜日", "25%"))
    col4.markdown(my_mkdwn("**3位**", f"月曜日", "12%"))

    labels = ["日", "土", "月", "水", "火", "木", "金"]
    values = [30, 25, 14, 10, 13, 5, 6]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                sort=True,
                direction="clockwise",
                textposition="inside",
                textinfo="percent+label",
            )
        ]
    )

    colors = ["#636EFA", "#EF553B", "#00CC96", "gray", "gray", "gray", "gray"]
    fig.update_traces(
        marker=dict(colors=colors),
        textfont_size=20,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("## 人が多い時刻")
    col2, col3, col4 = st.columns([1, 1, 1])

    col2.markdown(my_mkdwn("**1位**", f"11時", "15%"))
    col3.markdown(my_mkdwn("**2位**", f"12時", "10%"))
    col4.markdown(my_mkdwn("**3位**", f"13時", "9%"))

    char_data1 = pd.DataFrame(
        np.array(
            [
                0,
                1,
                2,
                5,
                6,
                6,
                7,
                10,
                12,
                13,
                17,
                18,
                17,
                15,
                10,
                9,
                9,
                8,
                6,
                4,
                3,
                2,
                1,
                0,
            ]
        ),
        columns=["count"],
    )
    char_data1["data"] = "先週"

    df = pd.concat([char_data1])

    fig = px.line(df, x=df.index, y="count", markers=True)

    st.plotly_chart(fig, use_container_width=True)

    # st.title(place_name)
    # image = Image.open(pic_url)
    # st.title(pic_url)
    # st.image(image, caption=place_name)

    # fig = draw_data(sss.df_day, hol_edge, "countingDirection")
    # st.plotly_chart(fig, use_container_width=True)

    # comp_input_trend(place_name, sss.df_day, params)
    # comp_csv_trend(place_name, sss.df_day)
