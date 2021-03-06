import time
import urllib.parse
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from apps.utils import load_date, set_params, upload_csv
from multiapp import MultiApp

OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]


def app():
    # load data
    URL = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E3%81%BE%E3%82%8B%E3%81%A3%E3%81%A8%E3%83%97%E3%83%A9%E3%82%B6.csv"

    DF = pd.read_csv(URL)
    DF = DF[DF["area"] == "plaza_car_near"]
    DF.day = pd.to_datetime(DF.day)

    st.title(urllib.parse.unquote(f'{URL.split("/")[-1].split(".")[0].split("_")[-1]}'))

    # set sidebar
    obj_type_selector = st.sidebar.selectbox(
        "Select your aaaaaaafavorite flower", OBJ_TYPE
    )

    def obj_type(df, obj_type_selector):
        df = df[df["name"] == obj_type_selector]

        fig = px.line(df, x="day", y="timestamp", color="countingDirection")
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="数",
            xaxis_tickformat="%Y-%m-%d",
        )
        fig.add_vrect(
            x0="2021-08-01",
            x1="2021-08-06",
            fillcolor="Red",
            opacity=0.5,
            layer="below",
            line_width=0,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.table(df)

    obj_type(DF, obj_type_selector)
