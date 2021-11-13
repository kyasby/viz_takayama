import streamlit as st

# import streamlit.session_state as sss

sss = st.session_state

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from statsmodels.tsa.seasonal import STL

from apps.utils import combine_df, load_date, set_params, show_title, upload_csv

OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]


def draw_date(df):

    fig = px.bar(
        df,
        x="week",
        y="timestamp",
        color='week',
        color_discrete_sequence=["#EF553B", "#EF553B", "#636EFA", "#636EFA", "#636EFA", "#636EFA", "#636EFA"],
    )

    fig.update_layout(
        legend=dict(
            x=0.002,
            y=0.998,
            xanchor="left",
            yanchor="top",
            orientation="h",
        ),
        legend_title_text="",
    )

    st.plotly_chart(fig, use_container_width=True)


def draw_comparison(place_name, place_df):
    with st.expander("自分のデータをアップロードして，この地点のデータと比べる"):
        st.markdown(
            "`曜日と数値を含むcsv`をアップロードすると，比較をすることができます。\
                  例えば，通行人の人数が増えている曜日に，売り上げも増えているか比較することができます。"
        )

        st.markdown(
            "日付：`月曜`のような形式にしてください。例：`月曜`\
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
            fig = px.line(
                sss.df_combi_df_week,
                y="timestamp",
                color="type",
                title=f"大まかな変化の比較({place_name})",
            )

            sss.combined_graph_week = fig
        if "combined_graph_week" in sss:
            st.plotly_chart(sss.combined_graph_week)


def app():
    params = set_params()
    pic_url, place_name, sss.df_week, hol_edge = load_date("week", params)

    st.title(place_name)
    image = Image.open(pic_url)
    st.image(image, caption=place_name)
    draw_date(sss.df_week)
    draw_comparison(place_name, sss.df_week)


# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text1.csv --fields ‘timestamp,recordingId’ --query '{"timestamp": {"$gte":{"$date": "2021-09-27T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-10-30T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text2.csv --fields ‘recordingId’ --query '{"timestamp": {"$gte":{"$date": "2021-10-01T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-10-02T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text3.csv --fields 'recordingId' --query '{"timestamp": {"$gte":{"$date": "2021-10-03T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-10-05T23:59:00.000Z"}}}'
# mongoexport --port 27017 --db opendatacam --collection tracker --type csv --out ./text4.csv --fields 'timestamp, recordingId' --query '{"timestamp": {"$gte":{"$date": "2021-10-06T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-10-10T23:59:00.000Z"}}}'
