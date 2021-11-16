import streamlit as st

sss = st.session_state

from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image

from apps.utils import combine_df, load_date, set_params, upload_csv


# 選択場所のグラフを描く
@st.experimental_memo
def draw_data(df, hol_edge, color):

    fig = px.line(df, x="day", y="timestamp", markers=True)

    fig.update_layout(
        xaxis_title="日付",
        yaxis_title="数",
        xaxis_tickformat="%Y-%m-%d",
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            orientation="h",
        ),
        yaxis={"range": (df["timestamp"].min() * 0.1, df["timestamp"].max() * 1.1)},
        # ),
        legend_title_text="",
    )
    fig.update_layout(template="seaborn")  # 白背景のテーマに変更

    if hol_edge:
        # 休日に背景色
        it = iter(hol_edge)
        for start, end in zip(it, it):
            fig.add_vrect(
                x0=str(start)[:10],
                x1=str(end)[:10],
                fillcolor="red",
                opacity=0.2,
                layer="below",
                line_width=0,
            )
    return fig


@st.experimental_memo
def draw_trend(df, place_name):
    fig = px.line(
        df,
        y="trend",
        color="type",
        title=f"大まかな変化の比較({place_name})",
    )
    fig.update_layout(
        xaxis_title="日付",
        yaxis_title="増減",
        xaxis_tickformat="%Y-%m-%d",
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            orientation="h",
        ),
        legend_title_text="",
        yaxis={
            "range": (
                df["trend"].min() * 0.1,
                df["trend"].max() * 1.1,
            )
        },
    )
    return fig


# トレンドのグラフを描く(csvデータ)
def comp_csv_trend(place_name, place_df):

    with st.expander("自分のデータをアップロードして，この地点のデータと比べる"):
        st.markdown(
            "`日付と数値を含むcsv`をアップロードすると，通行人のトレンドと比較することができます。\
                トレンドとは，大まかな増減の傾向のことです。\
                例えば，通行人の人数が増えている際に，売り上げも増えているか比較することができます。"
        )

        st.markdown(
            "日付：`yyyy-mm-dd`の形式にしてください。例：`2021-01-29`\
                \n 数値：数字のみ入れてください。少数も可能です。"
        )

        show_csv_sample = st.radio(
            "アップロードするcsvのサンプル", ("表示", "非表示"), index=1, key="tmp1"
        )
        if show_csv_sample == "表示":
            st.dataframe(place_df.head(3))

        [*tmp] = upload_csv("day")

        if len(tmp) == 3:
            sss.uploaded_df_day, sss.count_col, sss.day_col = tmp

        if "day_col" in sss:

            # プレビュ
            st.markdown("アップロードファイルのプレビュー")
            st.dataframe(sss.uploaded_df_day.head(3))

            sss.df_combi_df_day = combine_df(
                "day",
                place_name,
                place_df,
                sss.uploaded_df_day,
                sss.count_col,
                sss.day_col,
                True,
            )

            sss.combined_graph_day = draw_trend(sss.df_combi_df_day, place_name)
        if "combined_graph_day" in sss:
            st.plotly_chart(sss.combined_graph_day)


# トレンドのグラフを描く(inputデータ)
def comp_input_trend(place_name, place_df, params):
    with st.expander("データを入力して，この地点のデータと比べる"):

        st.markdown("日付に対応する数字を入れてください。")

        date_start = params["date_start"]
        date_end = params["date_end"]
        days = (date_end - date_start).days + 1

        datelist = [date_start + timedelta(days=x) for x in range(days)]

        col1, col2, col3 = st.columns(3)

        num = len(datelist) // 3

        sss.input_dict = {}
        for d in datelist[:num]:
            sss.input_dict[d] = col1.text_input(str(d), help="help", key=d)

        for d in datelist[num * 1 : num * 2]:
            sss.input_dict[d] = col2.text_input(str(d), key=d)

        for d in datelist[num * 2 :]:
            sss.input_dict[d] = col3.text_input(str(d), key=d)

        # 数字以外が入った時対策
        for k, v in sss.input_dict.items():
            if v:
                try:
                    sss.input_dict[k] = float(v)
                except ValueError:
                    st.error(f"{k}に変な値が入っています。数字を入力してね")
                except Exception as e:
                    st.error(f"予期せぬエラーです。ページを再読み込みしてみてください。{e}")
            sss.input_dict[k] = 10

        if st.button("比較する"):
            for k, v in sss.input_dict.items():
                try:
                    float(v)
                except:
                    st.error(f"{k}に値が入っていないよ！")
                    st.stop()

            df = (
                pd.DataFrame(sss.input_dict, index=["timestamp"])
                .T.reset_index()
                .rename(columns={"index": "day"})
            )

            # 10以上なら，トレンド抽出する
            if len(sss.input_dict) >= 10:
                df_combi_df_day = combine_df(
                    "day", place_name, place_df, df, "timestamp", "day", True
                )
                sss.combined_graph_day = draw_trend(df_combi_df_day, place_name)
                if "combined_graph_day" in sss:
                    st.plotly_chart(sss.combined_graph_day)

            # データが10未満なら，そのまま表示する
            else:
                hol_edge = place_df[place_df["is_edge_holiday"] == 1]["day"]
                df_combi_df_day = combine_df(
                    "day", place_name, place_df, df, "timestamp", "day", False
                )
                df_combi_df_day = df_combi_df_day.reset_index().rename(
                    columns={"index": "day"}
                )
                fig = draw_data(df_combi_df_day, hol_edge, "type")
                st.plotly_chart(fig, use_container_width=True)


def app():
    params = set_params()
    pic_url, place_name, sss.df_day, hol_edge = load_date("day", params)

    st.write(sss.df_day)

    st.title(params["place"])
    image = Image.open(pic_url)
    st.image(image, caption=place_name)

    fig = draw_data(sss.df_day, hol_edge, "countingDirection")
    st.plotly_chart(fig, use_container_width=True)

    comp_input_trend(place_name, sss.df_day, params)
    comp_csv_trend(place_name, sss.df_day)
