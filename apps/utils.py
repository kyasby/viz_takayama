import time

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import urllib.parse


OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]


# 後から綺麗にする
@st.cache()
def load_date(params):

  if params["place"] == "マルプ":
    url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E3%81%BE%E3%82%8B%E3%81%A3%E3%81%A8%E3%83%97%E3%83%A9%E3%82%B6.csv"
    area = "plaza_car_near"
  else:
    url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E6%9C%9B%E9%81%A0.csv"
    area = "juroku_zoom"
  
  df = pd.read_csv(url)
  df.day = pd.to_datetime(df.day)

  # カウント線を絞る
  df = df[df["area"]==area]

  # 種類を絞る
  df = df[df["name"] == params["obj_type_selector"]]

  df = df[(pd.to_datetime(params["date_start"]) < df.day) & (df.day  < pd.to_datetime(params["date_end"]))]

  # 休日の前後リスト
  hol_edge = df[df["is_edge_holiday"]==1]["day"]
  hol_edge = sorted(hol_edge.unique())


  return url, df, hol_edge

def set_params():
  global obj_type_selector, date_start, date_end, place

  place = st.sidebar.selectbox("場所を選んでください。", ["マルプ", "16"])

  obj_type_selector = st.sidebar.selectbox("Select your favorite flower", OBJ_TYPE)

  date_start = st.sidebar.date_input('開始日',
                               min_value=date(2021,6,26),
                               max_value=date(2021,9,3),
                               value=date(2021, 7, 1),
  )

  date_end   = st.sidebar.date_input('終了日',
                               min_value=date(2021,6,26),
                               max_value=date(2021,9,3),
                               value=date(2021, 9, 3),
  )

  df = pd.DataFrame(
          {"English": ["January", "Feburary","March", "April",
                       "May", "June", "July", "August", "September", "October", "November", "December"],
           "日本語": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]}
   ).set_index("日本語")

  st.sidebar.table(df) 

  params={"obj_type_selector": obj_type_selector,
          "date_start": date_start,
          "date_end": date_end,
          "place": place

  }

  return params

def upload_csv(type):

  csv = st.file_uploader("ファイルアップロード", type='csv')
  if csv:
    df = pd.read_csv(csv)

    #　カラム入力
    columns = df.columns
    count_col = st.selectbox("比較する値のカラム名を入れてください。", columns)
    if type == "day":
      day_col = st.selectbox("日付のカラム名を入れてください。", columns)
      if count_col and day_col:
        try:
          df["day"] = pd.to_datetime(df[day_col])
        except KeyError as e:
          st.error("日付のカラムを正しく入力してください。")
        else:
          return df, count_col, day_col
    elif type == "week":
      day_col = st.selectbox("週のカラム名を入れてください。", columns)

  return [None]

      
 