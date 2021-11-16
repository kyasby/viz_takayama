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

config = {"staticPlot": True}

# <span style='color: red;'></span>
def my_mkdwn(txt1, txt2, txt3=None):
    text = f"**{txt1}**  \n### {txt2}"
    if txt3:
        return text + f"\n #### {txt3}"
    else:
        return text


def pedestrian(params,df_last, df_this):

    count_last = df_last.iloc[:len(df_this)]["timestamp"].sum()
    count_this = df_this["timestamp"].sum()

    ratio = count_this / count_last
    this_last_week = df_this.iloc[-1]["week"]

    if ratio > 1:
        color = "green"
        code  = "+"
    else:
        color = "red"
        code  = "-"

    st.markdown("## 通行人数")
    st.write(f"＊以下は，日曜〜{this_last_week}までの比較")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    col1.markdown(my_mkdwn("先週", f"{count_last}人"))
    col2.markdown(my_mkdwn("今週", f"{count_this}人"))
    col3.markdown(
        my_mkdwn("先週と今週の比較", f'<span style="color: {color};">{code}{(100-ratio*100):.1f}%</span>'),
        unsafe_allow_html=True,
    )

    fig = pedestrian_graph(df_last, df_this)
    col4.plotly_chart(fig, use_container_width=True, **{"config": config})


def pedestrian_graph(df_last, df_this):
    df_last["週"] = "先週"
    df_this["週"] = "今週"

    df = pd.concat([df_last, df_this])

    fig = px.line(
        df,
        x="week",
        y="timestamp",
        color="週",
        markers=True,
        width=500,
        height=200,
    )
    fig.update_layout(
        xaxis_title="曜日",
        yaxis_title="通行人",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def week(df):
    df = df.reset_index()
    first  = df.iloc[-1]
    second = df.iloc[-2]
    third  = df.iloc[-3]
    three_sum = df.iloc[-3:].sum()

    st.markdown("## 人が多い曜日")

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

    col1.markdown(my_mkdwn("1位", f"{first['week']}日",  f"{first['percentage']*100:.1f}%"))
    col2.markdown(my_mkdwn("2位", f"{second['week']}日", f"{second['percentage']*100:.1f}%"))
    col3.markdown(my_mkdwn("3位", f"{third['week']}日",  f"{third['percentage']*100:.1f}%"))
    col4.markdown(my_mkdwn("合計", f"合計",  f"{three_sum['percentage']*100:.1f}%"))

    fig = week_graph(df)
    col5.plotly_chart(fig, use_container_width=True, **{"config": config})


def week_graph(df):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["week"],
                values=df["timestamp"],
                sort=True,
                direction="clockwise",
                textposition="inside",
                textinfo="percent+label",
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        width=500,
        height=200,
        showlegend=False,
    )
    colors = ["gray", "gray", "gray", "gray", "#636EFA", "#EF553B", "#00CC96", ]
    fig.update_traces(
        marker=dict(colors=colors),
        textfont_size=20,
    )

    return fig


def time(df):
    df_mean = df.groupby("time").mean().reset_index()
    df_sorted = df_mean.sort_values(by="timestamp")
    
    sum_time = df_mean["timestamp"].sum()
    df_sorted["percentage"] = df_sorted["timestamp"] / sum_time

    first     = df_sorted.iloc[-1]
    second    = df_sorted.iloc[-2]
    third     = df_sorted.iloc[-3]
    three_sum = df_sorted.iloc[-3:].sum()

    st.markdown("## 人が多い時刻")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

    col1.markdown(my_mkdwn("1位", f"{first['time']}時",  f"{first['percentage'] *100:.1f}%"))
    col2.markdown(my_mkdwn("2位", f"{second['time']}時", f"{second['percentage']*100:.1f}%"))
    col3.markdown(my_mkdwn("3位", f"{third['time']}時",  f"{third['percentage'] *100:.1f}%"))
    col4.markdown(my_mkdwn("合計", f"合計",  f"{three_sum['percentage'] *100:.1f}%"))

    fig = time_graph(df)
    col5.plotly_chart(fig, use_container_width=True, **{"config": config})


def time_graph(df):

    fig = px.line(
        df,
        x=df["time"],
        y=df["timestamp"],
        color=df["is_holiday"],
        markers=True,
        width=500,
        height=200,
    )

    fig.update_layout(
        xaxis_title="時刻",
        yaxis_title="通行人",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def app():
    # 全体設定
    st.markdown(
        f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: {1000}px;
            padding-top: {1}rem;
            padding-right: {1}rem;
            padding-left: {1}rem;
            padding-bottom: {10}rem;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )
    params = set_params()
    pic_url, place_name, sss.df_summary, hol_edge = load_date("day", params)


    # 通行人数
    st.markdown("---")
    f = sss.df_summary["week"]=="日曜"
    last_sun = sss.df_summary.iloc[-15:][f]
    snd_last_sun_day = last_sun["day"].iloc[-2]
    last_sun_day     = last_sun["day"].iloc[-1]

    df_last = sss.df_summary[(snd_last_sun_day<=pd.to_datetime(sss.df_summary["day"]))
                            &(pd.to_datetime(sss.df_summary["day"]) < last_sun_day)]
    df_this = sss.df_summary[last_sun_day<=pd.to_datetime(sss.df_summary["day"])]

    st.title(f'{params["place"]}の分析の概要')
    pedestrian(params, df_last, df_this)


    # 人が多い曜日
    st.markdown("---")
    df_med = sss.df_summary.groupby("week").median()
    sum_ts = df_med["timestamp"].sum()
    df_med["percentage"] = df_med["timestamp"] / sum_ts
    df_med = df_med.sort_values(by="percentage")
    week(df_med)

    # 人が多い時刻
    _, _, sss.df_time, _ = load_date("time", params)

    st.markdown("---")
    time(sss.df_time)
