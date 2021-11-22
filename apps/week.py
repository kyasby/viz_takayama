import streamlit as st

# import streamlit.session_state as sss

sss = st.session_state

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from statsmodels.tsa.seasonal import STL

from apps.global_var import CONFIG
from apps.utils import combine_df, load_date, set_params, upload_csv

OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]


def draw_date(df):

    fig = px.bar(
        df,
        x="week",
        y="count",
        color="week",
        color_discrete_sequence=[
            "#EF553B",
            "#636EFA",
            "#636EFA",
            "#636EFA",
            "#636EFA",
            "#636EFA",
            "#EF553B",
        ],
    )

    fig.update_layout(
        xaxis_title="曜日",
        yaxis_title="通行人数",
        legend=dict(
            x=0.002,
            y=0.999,
            xanchor="left",
            yanchor="top",
            orientation="h",
        ),
        font=dict(size=18),
        legend_title_text="",
        yaxis={"range": (0, df["count"].max() * 1.3)}
    )

    st.plotly_chart(fig, use_container_width=True, **{"config": CONFIG})


def draw_comparison(place_name, place_df):
    with st.expander("自分のデータをアップロードして，この地点のデータと比べる"):
        st.markdown(
            "`日時と数値を含むcsv`をアップロードすると，比較をすることができます。\
                  例えば，通行人の人数が増えている曜日に，売り上げも増えているか比較することができます。"
        )

        st.markdown(
            "日付：`yyyy-mm-dd HH:mm`の形式にしてください。例：`2021-01-29 17:00`\
                \n 数値：数字のみ入れてください。少数も可能です。"
        )

        show_csv_sample = st.radio("アップロードするcsvのサンプル", ("表示", "非表示"), index=1)
        if show_csv_sample == "表示":
            st.dataframe(place_df.head(3))

        [*tmp] = upload_csv("week")

        if len(tmp) == 3:
            sss.uploaded_df_week, sss.count_col, sss.day_col = tmp

        if "day_col" in sss:
            # プレビュ
            st.markdown("アップロードファイルのプレビュー")
            st.dataframe(sss.uploaded_df_week.head(3))

            sss.df_combi_df_week = combine_df(
                "week",
                place_name,
                place_df,
                sss.uploaded_df_week,
                sss.count_col,
                sss.day_col,
            )

            st.table(sss.df_combi_df_week)
            fig = px.bar(
                sss.df_combi_df_week,
                y="count",
                color="type",
                title=f"大まかな変化の比較({place_name})",
                barmode="group",
            )
            fig.update_layout(
                xaxis_title="曜日",
                yaxis_title="通行人数",
                legend=dict(
                    x=0.002,
                    y=0.999,
                    xanchor="left",
                    yanchor="top",
                    orientation="h",
                ),
                font=dict(size=18),
                legend_title_text="",
                yaxis={"range": (0, sss.df_combi_df_week["count"].max() * 1.3)}
            )

            sss.combined_graph_week = fig
        if "combined_graph_week" in sss:
            st.plotly_chart(sss.combined_graph_week, use_container_width=True, **{"config": CONFIG})


def app():
    params = set_params()
    pic_url, place_name, sss.df_week, hol_edge = load_date("week", params)
    st.title(params["place"])
    image = Image.open(pic_url)
    st.image(image, caption=params["place"])
    draw_date(sss.df_week)
    draw_comparison(params["place"], sss.df_week)


# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text1.csv --fields ‘count,recordingId’ --query '{"count": {"$gte":{"$date": "2021-09-27T00:00:00.000Z"}}, "count": {"$lte": {"$date": "2021-10-30T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text2.csv --fields ‘recordingId’ --query '{"count": {"$gte":{"$date": "2021-10-01T00:00:00.000Z"}}, "count": {"$lte": {"$date": "2021-10-02T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text3.csv --fields 'recordingId' --query '{"count": {"$gte":{"$date": "2021-10-03T00:00:00.000Z"}}, "count": {"$lte": {"$date": "2021-10-05T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text4.csv --fields 'count, recordingId' --query '{"count": {"$gte":{"$date": "2021-10-06T00:00:00.000Z"}}, "count": {"$lte": {"$date": "2021-10-10T23:59:00.000Z"}}}'
