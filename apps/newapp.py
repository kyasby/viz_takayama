import time

import streamlit as st
# import streamlit.session_state as sss

sss = st.session_state

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from multiapp import MultiApp
import urllib.parse
from statsmodels.tsa.seasonal import STL


from apps.utils import load_date, set_params, upload_csv


#選択場所のグラフを描く
def draw_data(df, hol_edge, params):

  fig = px.line(df, x='day', y="timestamp", color="countingDirection")

  # add_data
  # df_add = df[df["countingDirection"]=="leftright_topbottom"]
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


# トレンドのグラフを描く
def draw_trend(place_name, place_df):

  @st.cache(suppress_st_warning=True)
  def combine_df(place_df, uploaded, count_col, day_col):

    def convert_df(df, type_name, count_col, day_col="day"):
      # resample todo: 不要では？
      df = df.set_index("day")
      df = df.resample(dim).sum()

      # トレンド抽出
      try:
        stl=STL(df[col], period=period, robust=True)
      except KeyError as e:
        st.error('比較するカラム名を正しく入れてください!')
      else:
        stl_series = stl.fit()
      return pd.DataFrame(stl_series.trend)

    place_df = convert_df(place_df, place_name, "timestamp")
    uploaded = convert_df(uploaded, "アップロードされたデータ", count_col, day_col)

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

    [*tmp] = upload_csv("day")

    if tmp[0] is not None or "uploaded_df" in sss:
      if len(tmp) == 3:
        sss.uploaded_df, sss.count_col, sss.day_col = tmp

      #プレビュ
      st.markdown("アップロードファイルのプレビュー")
      st.dataframe(sss.uploaded_df.head(3))

      sss.df_combi_df_day = combine_df(place_df, sss.uploaded_df, sss.count_col, sss.day_col)

      fig = px.line(sss.df_combi_df_day, y="trend", color="type", title=f"大まかな変化の比較({place_name})")
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
      sss.combined_graph = fig
    if "combined_graph" in sss:
      st.plotly_chart(sss.combined_graph, use_container_width=True)


def app():

  params = set_params()
  url, sss.df_day, hol_edge = load_date(params)

  place_name = urllib.parse.unquote(f'{url.split("/")[-1].split(".")[0].split("_")[-1]}')
  st.title(place_name)

  draw_data(sss.df_day, hol_edge, params)
  draw_trend(place_name, sss.df_day)


