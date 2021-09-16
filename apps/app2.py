import time

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from multiapp import MultiApp


OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]

def app():
  # load data
  URL = "/Users/ryo/Documents/Lab/Jetson/jetson_csv/9-3/day_grouped_by_まるっとプラザ.csv"
  DF = pd.read_csv(URL)
  DF = DF[DF["area"]=="plaza_car_near"]
  DF.day = pd.to_datetime(DF.day)


  st.title(f'{URL.split("/")[-1].split(".")[0].split("_")[-1]}')


  # set sidebar
  obj_type_selector = st.sidebar.selectbox("Select your aaaaaaafavorite flower", OBJ_TYPE)


  def obj_type(df, obj_type_selector):
      df = df[df["name"] == obj_type_selector]
      df = df[(pd.to_datetime(date_start) < df.day) & (df.day  < pd.to_datetime(date_end))]


      fig = px.line(df, x='day', y="timestamp", color="countingDirection")
      fig.update_layout(xaxis_title="日付",
                        yaxis_title="数",
                        xaxis_tickformat = '%Y-%m-%d',)
      st.plotly_chart(fig, use_container_width=True)

  obj_type(DF, obj_type_selector)

