import streamlit as st

sss = st.session_state

from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image
from jp_holiday import jp_holiday

from apps.global_var import CONFIG
from apps.utils import combine_df, load_date, set_params, upload_csv


# 選択場所のグラフを描く
@st.experimental_memo
def draw_data(df, color):

    fig = px.line(df, x="time", y="count", color=color, markers=True)

    fig.update_layout(
        xaxis_title="時刻",
        yaxis_title="数",
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            orientation="h",
        ),
        yaxis={"range": (df["count"].min() * 0.1, df["count"].max() * 1.1)},
        # ),
        legend_title_text="",
    )
    fig.update_layout(template="seaborn")  # 白背景のテーマに変更

    return fig


@st.experimental_memo
def draw_trend(df, place_name):
    fig = px.line(
        df,
        y="count",
        color="type",
        title=f"大まかな変化の比較({place_name})",
    )
    fig.update_layout(
        xaxis_title="日付",
        yaxis_title="増減",
        # xaxis_tickformat="%Y-%m-%d",
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
                df["count"].min() * 0.1,
                df["count"].max() * 1.1,
            )
        },
    )
    return fig


# トレンドのグラフを描く(csvデータ)
def comp_csv_trend(place_name, place_df):

    with st.expander("自分のデータをアップロードして，この地点のデータと比べる"):
        st.markdown(
            "`日付と数値を含むcsv`をアップロードすると，選択場所と比較することができます。\
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

            sss.uploaded_df_day = jp_holiday.is_holiday(sss.uploaded_df_day, sss.day_col, "is_holiday")

            sss.df_combi_df_day = combine_df(
                "time",
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
def comp_input_trend(place_df, params):
    with st.expander("データを入力して，この地点のデータと比べる"):

        st.markdown("日付に対応する数字を入れてください。")

        col1, col2, col3 = st.columns(3)

        num = 24

        sss.input_dict = {}
        for d in range(8):
            sss.input_dict[d] = col1.text_input(str(d) + "時", key=d)

        for d in range(8, 16):
            sss.input_dict[d] = col2.text_input(str(d) + "時", key=d)

        for d in range(16, 24):
            sss.input_dict[d] = col3.text_input(str(d) + "時", key=d)

        # 数字以外が入った時対策
        for k, v in sss.input_dict.items():
            if v:
                try:
                    sss.input_dict[k] = float(v)
                except ValueError:
                    st.error(f"{k}時に変な値が入っています。数字を入力してね")
                except Exception as e:
                    st.error(f"予期せぬエラーです。ページを再読み込みしてみてください。{e}")
            sss.input_dict[k] = 10  # for debug

        if st.button("比較する"):
            for k, v in sss.input_dict.items():
                try:
                    float(v)
                except:
                    st.error(f"{k}に値が入っていないよ！")
                    st.stop()

            df = (
                pd.DataFrame(sss.input_dict, index=["count"])
                .T.reset_index()
                .rename(columns={"index": "time"})
            )
            df["is_holiday_x"] = "uploaded_data"

            df_combi_df_day = combine_df(
                "time", params["place"], place_df, df, "count", "index", False
            )

            df_combi_df_day = df_combi_df_day.reset_index()

            fig = draw_data(df_combi_df_day, "is_holiday_x")
            st.plotly_chart(fig, use_container_width=True, **{"config": CONFIG})


def app():
    params = set_params()
    pic_url, place_name, sss.df_day, hol_edge = load_date("time", params)

    st.title(params["place"])
    image = Image.open(pic_url)
    st.image(image, caption=params["place"])

    fig = draw_data(sss.df_day, "is_holiday_x")
    st.plotly_chart(fig, use_container_width=True, **{"config": CONFIG})

    comp_input_trend(sss.df_day, params)
    comp_csv_trend(params["place"], sss.df_day)
