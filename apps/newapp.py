import time

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from multiapp import MultiApp
import urllib.parse
from statsmodels.tsa.seasonal import STL


OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]



def app():


  def set_params():
    # set sidebar
    global obj_type_selector, date_start, date_end, place
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
    place = st.sidebar.selectbox("場所を選んでください。", ["マルプ", "16"])

    params={"obj_type_selector": obj_type_selector,
            "date_start": date_start,
            "date_end": date_end,
            "place": place

    }
    return params


  @st.cache()
  def load_date(parama):

    # 後から綺麗にする
    if params["place"] == "マルプ":
      url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E3%81%BE%E3%82%8B%E3%81%A3%E3%81%A8%E3%83%95%E3%82%9A%E3%83%A9%E3%82%B5%E3%82%99.csv"
      area = "plaza_car_near"
    else:
      url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E6%9C%9B%E9%81%A0.csv"
      area = "juroku_zoom"


    df = pd.read_csv(url)
    df.day = pd.to_datetime(df.day)
    df = df[df["area"]==area]

    df = df[df["name"] == params["obj_type_selector"]]

    if params["place"]=="マルプ":
      df = df[(pd.to_datetime(params["date_start"]) < df.day) & (df.day  < pd.to_datetime(params["date_end"]))]
    else:
      df = df[(pd.to_datetime(params["date_start"]) < pd.to_datetime(df.date)) & (pd.to_datetime(df.date)  < pd.to_datetime(params["date_end"]))]

    return url, df


  def obj_type(df, params):

    fig = px.line(df, x='day', y="timestamp", color="countingDirection")

    # add_data
    df_add = df[df["countingDirection"]=="leftright_topbottom"]
    # fig.add_trace(go.Scatter(x=df_add["day"], y=df_add["timestamp"], name='your data'))

    fig.update_layout(xaxis_title="日付",
                      yaxis_title="数",
                      xaxis_tickformat = '%Y-%m-%d',)
    fig.add_vrect(
        x0="2021-08-01", x1="2021-08-06",
        fillcolor="LightSalmon", opacity=0.5,
        layer="below", line_width=0,
    )
    st.plotly_chart(fig, use_container_width=True)


  def draw_trend(original):

    def upload_csv():
      global count_col
      global day_col
      
      csv = st.file_uploader("ファイルアップロード", type='csv')
      if csv:
        df = pd.read_csv(csv)
        st.table(df.head(3))
        count_col = st.text_input("比較する値のカラム名を入れてください。", value="timestamp") # todo default
        day_col   = st.text_input("日付のカラム名を入れてください。", value="date") # todo default
        if count_col and day_col:
          df["day"] = pd.to_datetime(df[day_col])
          return df


    @st.cache()
    def make_comparing_df(original, uploaded):

      @st.cache()
      def convert_df(df, day_col="day", dim="D"):
        df = df.set_index("day")
        df = df.resample(dim).sum()
        return df 

      def extract_trend(df, col, period=7):
        stl=STL(df[col], period=period, robust=True)
        stl_series = stl.fit()
        
        return pd.DataFrame(stl_series.trend) 

      original = convert_df(original)
      original = extract_trend(original, "timestamp")
      
      uploaded = convert_df(uploaded)
      uploaded = extract_trend(uploaded, count_col)

      original["trend"] /= original["trend"].max()
      uploaded["trend"] /= uploaded["trend"].max()

      original["type"] = "original"
      uploaded["type"] = "uploaded"

      df = pd.concat([original, uploaded], axis=0)

      return df

    with st.expander("自分のデータと比べる"):
      # st.markdown('日付と数値を含む`csv`をアップロードすると，通行人のトレンドと比較することができます。\
      #             \n 日付：`yyyy-mm-dd`の形式にしてください。例：2021-01-29\
      #             \n 数値：数字のみ入れてください。少数も可能です。')
      
      show_csv_sample = st.radio("アップロードするcsvのサンプル",
                                ('表示', '非表示'), index=1)
      if show_csv_sample == "表示":
        st.table(original.head(3))

      uploaded = upload_csv()
      if uploaded is not None:
        df = make_comparing_df(original, uploaded)

        fig = px.line(df, y="trend", color="type")
        st.plotly_chart(fig, use_containupler_width=True)




  params = set_params()
  url, df = load_date(params)
  st.title(urllib.parse.unquote(f'{url.split("/")[-1].split(".")[0].split("_")[-1]}'))
  obj_type(df, params)
  draw_trend(df)

