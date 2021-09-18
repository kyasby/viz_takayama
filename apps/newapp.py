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


def set_params():
  # set sidebar
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


# 後から綺麗にする
@st.cache()
def load_date(params):

  if params["place"] == "マルプ":
    url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E3%81%BE%E3%82%8B%E3%81%A3%E3%81%A8%E3%83%97%E3%83%A9%E3%82%B6.csv"
    area = "plaza_car_near"
    df = pd.read_csv(url)
    df.day = pd.to_datetime(df.day)
  else:
    url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E6%9C%9B%E9%81%A0.csv"
    area = "juroku_zoom"
    df = pd.read_csv(url)
    df.date = pd.to_datetime(df.date)
  
  df = df[df["area"]==area]

  # 種類を絞る
  df = df[df["name"] == params["obj_type_selector"]]

  if params["place"]=="マルプ":
    df = df[(pd.to_datetime(params["date_start"]) < df.day) & (df.day  < pd.to_datetime(params["date_end"]))]
  else:
    df = df[(pd.to_datetime(params["date_start"]) < pd.to_datetime(df.date)) & (pd.to_datetime(df.date)  < pd.to_datetime(params["date_end"]))]

  # 休日の前後リスト
  hol_edge = df[df["is_edge_holiday"]==1]["day"]
  hol_edge = sorted(hol_edge.unique())


  return url, df, hol_edge

#選択場所のグラフを描く
def draw_data(df, hol_edge, params):

  fig = px.line(df, x='day', y="timestamp", color="countingDirection")

  # add_data
  df_add = df[df["countingDirection"]=="leftright_topbottom"]
  # fig.add_trace(go.Scatter(x=df_add["day"], y=df_add["timestamp"], name='your data'))

  fig.update_layout(xaxis_title = "日付",
                    yaxis_title = "数",
                    xaxis_tickformat = '%Y-%m-%d'
  )

  fig.update_layout(legend=dict(x = 0.01,
                                y = 0.99,
                                xanchor = 'left',
                                yanchor = 'top',
                                orientation = 'h',),
                    legend_title_text=''
  )

  # 休日に背景色
  it = iter(hol_edge)
  for start, end in zip(it, it):
    fig.add_vrect(
        x0=str(start)[:10], x1=str(end)[:10],
        fillcolor="LightSalmon", opacity=0.2,
        layer="below", line_width=0,
    )

  st.plotly_chart(fig, use_container_width=True)

# トレンドのラインを描く
def draw_trend(place_name, place_df):

  def upload_csv():
    global count_col
    global day_col
    
    csv = st.file_uploader("ファイルアップロード", type='csv')
    if csv:
      df = pd.read_csv(csv)

      # プレビュ
      st.markdown("アップロードファイルのプレビュー")
      st.dataframe(df.head(3))

      #　カラム入力
      columns = df.columns
      count_col = st.selectbox("比較する値のカラム名を入れてください。", columns)
      day_col = st.selectbox("日付のカラム名を入れてください。", columns)
      # count_col = st.text_input("比較する値のカラム名を入れてください。", value="timestamp") # todo default
      # day_col   = st.text_input("日付のカラム名を入れてください。", value="date") # todo default
      if count_col and day_col:
        try:
          df["day"] = pd.to_datetime(df[day_col])
        except KeyError as e:
          st.error("日付のカラムを正しく入力してください。")
        else:
          return df


  @st.cache(suppress_st_warning=True)
  def combine_df(place_df, uploaded):

    def convert_df(df, day_col="day", dim="D"):
      df = df.set_index("day")
      df = df.resample(dim).sum()
      return df 

    def extract_trend(df, col, period=7):
      try:
        stl=STL(df[col], period=period, robust=True)
      except KeyError as e:
        st.error('比較するカラム名を正しく入れてください!')
      else:
        stl_series = stl.fit()
      
      return pd.DataFrame(stl_series.trend) 

    place_df = convert_df(place_df)
    place_df = extract_trend(place_df, "timestamp")
    
    uploaded = convert_df(uploaded)
    uploaded = extract_trend(uploaded, count_col)

    # 最大値との比にする
    place_df["trend"] /= place_df["trend"].max()
    uploaded["trend"] /= uploaded["trend"].max()

    place_df["type"] = place_name
    uploaded["type"] = "アップロードされたデータ"

    df = pd.concat([place_df, uploaded], axis=0)

    return df

  with st.expander("自分のデータをアップロードして，この地点のデータと比べる"):
    st.markdown('`日付と数値を含むcsv`をアップロードすると，通行人のトレンドと比較することができます。\
                例えば，通行人の人数が増えている際に，売り上げも増えているか比較することができます。'
    )

    st.markdown('日付：`yyyy-mm-dd`の形式にしてください。例：`2021-01-29`\
                \n 数値：数字のみ入れてください。少数も可能です。'
    )
    
    show_csv_sample = st.radio("アップロードするcsvのサンプル", ('表示', '非表示'), index=1)
    if show_csv_sample == "表示":
      st.dataframe(place_df.head(3))

    uploaded_df = upload_csv()
    if uploaded_df is not None:
      df = combine_df(place_df, uploaded_df)

      fig = px.line(df, y="trend", color="type", title=f"大まかな変化の比較({place_name})")
      fig.update_layout(xaxis_title="日付",
                        yaxis_title="増減",
                        xaxis_tickformat = '%Y-%m-%d',
                        legend=dict(x = 0.01,
                                y = 0.99,
                                xanchor = 'left',
                                yanchor = 'top',
                                orientation = 'h',),
                        legend_title_text=''
      )
      st.session_state.combined_graph = fig
    if "combined_graph" in st.session_state:
      st.plotly_chart(st.session_state.combined_graph, use_container_width=True)


def app():

  params = set_params()
  url, df, hol_edge = load_date(params)

  place_name = urllib.parse.unquote(f'{url.split("/")[-1].split(".")[0].split("_")[-1]}')
  st.title(place_name)

  draw_data(df, hol_edge, params)
  draw_trend(place_name, df)


