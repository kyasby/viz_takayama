import time
import urllib.parse
from datetime import date, timedelta

import pandas
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml
from statsmodels.tsa.seasonal import STL

OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]

# 後から綺麗にする
# @st.experimental_memo
def load_date(dim_type, params, two_weeks=False):

    with open("place.yaml") as f:
        obj = yaml.safe_load(f)

    place_obj = obj[params["place"]]
    # st.write(place_obj)
    pic_url   = place_obj["url"]["pic"]
    url       = place_obj["url"]["csv"]
    areas     = place_obj["area"]

    df = pd.read_csv(url)

    # カウント線を絞る TODO
    df = df[df["area"].isin(areas)]

    # 種類を絞る
    df = df[df["name"] == params["obj_type_selector"]]

    hol_edge = None

    df.day = pd.to_datetime(df.day)

    if two_weeks:
        # もう一回summaryで絞るからザルでも問題なし。
        df = df[(pd.to_datetime(params["date_end"] - timedelta(days=14)) <= df.day)
                & (df.day <= pd.to_datetime(params["today"]))
                ]        
    else:
        df = df[(pd.to_datetime(params["date_start"]) <= df.day)
                & (df.day <= pd.to_datetime(params["date_end"]))
                ]

    st.table(df.head())
    st.table(df.tail())
    if dim_type == "day":
        df = df[["day", "name", "count", "is_edge_holiday", "week"]] # weekもsummary用に必要
        df = (
            df.groupby(["day", "name", "week"])
            .sum()
            .reset_index()
        )

        # 休日の前後リスト
        hol_edge = df[df["is_edge_holiday"] >= 1]["day"]
        hol_edge = sorted(hol_edge.unique())

    elif dim_type == "week":
        df = df[["day", "week", "name", "count"]]
        df = df.groupby(["day", "week", "name"]).sum()
        df = df.groupby(["week", "name"]).mean().reset_index()

        l_order = ["日曜", "月曜", "火曜", "水曜", "木曜", "金曜", "土曜"]

        df['order'] = df['week'].apply(lambda x: l_order.index(x) if x in l_order else -1)
        df = df.sort_values(by="order")

    elif dim_type == "time":
        df = df[["is_holiday_x", "time", "count"]]
        df = df.groupby(["is_holiday_x", "time"]).mean().reset_index()
        df["is_holiday_x"] = df["is_holiday_x"].apply(lambda x: "休日" if x else "平日")

    return (
        pic_url,
        params["place"],
        df,
        hol_edge,
    )


def set_params(is_map=False):
    # global obj_type_selector, date_start, date_end, place

    if is_map:
        place = None
    else:
        place = st.sidebar.selectbox("場所を選んでください！", ["まるっとプラザ",
                                                             "十六銀行高山支店",
                                                             "中橋",
                                                             "陣屋前交差点",
                                                             "白川たばこ店",
                                                             "ハラサイクル"])

    obj_type_selector = (
        "person"  # st.sidebar.selectbox("Select your favorite flower", OBJ_TYPE)
    )

    # date_start = st.sidebar.date_input(
    #     "開始日",
    #     min_value=date(2021, 6, 26),
    #     max_value=date(2021, 9, 3),
    #     value=date(2021, 7, 1),
    # )

    # date_end = st.sidebar.date_input(
    #     "終了日",
    #     min_value=date(2021, 6, 26),
    #     max_value=date(2021, 10, 21),
    #     value=date(2021, 10, 21),
    # )

    DAY_TYPE = ["直近1週間", "直近2週間", "直近1ヶ月", "夏休み", "全期間"]
    date_type = st.sidebar.selectbox("日付を選んでください！", DAY_TYPE)

    # 指定した日付を含む
    today = date(2021, 11, 20)
    date_end = today
    if date_type == "直近1週間":
        date_start = date(2021, 11, 13)
    elif date_type == "直近2週間":
        date_start = date(2021, 11, 6)
    elif date_type == "直近1ヶ月":
        date_start = date(2021, 10, 20)
    elif date_type == "夏休み":
        date_start = date(2021, 7, 22)
        date_end = date(2021, 8, 31)
    elif date_type == "全期間":
        date_start = date(2021, 6, 26)


    # 日本語と英語の表
    # df = pd.DataFrame(
    #     {
    #         "English": [
    #             "January",
    #             "Feburary",
    #             "March",
    #             "April",
    #             "May",
    #             "June",
    #             "July",
    #             "August",
    #             "September",
    #             "October",
    #             "November",
    #             "December",
    #         ],
    #         "日本語": [
    #             "1月",
    #             "2月",
    #             "3月",
    #             "4月",
    #             "5月",
    #             "6月",
    #             "7月",
    #             "8月",
    #             "9月",
    #             "10月",
    #             "11月",
    #             "12月",
    #         ],
    #     }
    # ).set_index("日本語")

    # st.sidebar.table(df)

    with open("place.yaml") as f:
        obj = yaml.safe_load(f)

    place_obj = obj["まるっとプラザ"]
    url       = place_obj["url"]["csv"]

    st.sidebar.download_button("比較用のサンプルデータをダウンロードする", pd.read_csv(url).to_csv(), "サンプル.csv")

    params = {
        "obj_type_selector": obj_type_selector,
        "date_start": date_start,
        "date_end": date_end,
        "place": place,
        "today": today
    }
    return params


def upload_csv(dim_type):

    csv = st.file_uploader("ファイルアップロード", type="csv")
    if csv:
        df = pd.read_csv(csv)

        # 　カラム入力
        columns = df.columns

        if dim_type == "day":
            msg = "日付のカラム名を入れてください。"
        elif dim_type == "week":
            msg = "日付のカラム名を入れてください。"
        elif dim_type == "time":
            msg = "（日付と）時刻のカラム名を入れてください。"

        dim_col = st.selectbox(msg, columns)

        try:
            df[dim_col] = pd.to_datetime(df[dim_col])
        except:
            st.error("正しいカラムを入れてください。")
        else:
            count_col = st.selectbox("比較する値のカラム名を入れてください。", columns)
            return df, count_col, dim_col

    return [None]


def extract_trend(df, count_col, period):
    # トレンド抽出
    try:
        stl = STL(df[count_col], period=period, robust=True)
    except:
        st.error("比較するカラム名を正しく入れてください!")
        st.stop()
        return
    else:
        stl_series = stl.fit()
        df = pd.DataFrame(stl_series.trend)
    return df


def convert_df(
    dim_type,
    df,
    place_name,
    count_col,
    should_extract,
    dim_col="day",
    dim="D",
    period=7,
):

    if dim_type == "day":
        df[dim_col] = pd.to_datetime(df[dim_col])
        df = df.set_index(dim_col)
        df = df.resample(dim).sum()

        if should_extract:
            df = extract_trend(df, count_col, period)
            df["trend"] /= df["trend"].sum()
        else:
            df["count"] /= df["count"].sum()

    elif dim_type == "week":

        df = df.groupby(["week"]).sum()
        try:
            df[count_col] /= df[count_col].sum()
        except KeyError:
            st.stop()
        l_order = [
            "月曜",
            "火曜",
            "水曜",
            "木曜",
            "金曜",
            "土曜",
            "日曜",
        ]

        df["order"] = df.index
        df["order"] = df["order"].apply(
            lambda x: l_order.index(x) if x in l_order else -1)
        df = df.sort_values("order")

    elif dim_type == "time":
        df = df.groupby(["time"]).mean()

    df["type"] = place_name

    return df


@st.experimental_memo(suppress_st_warning=True)
def combine_df(
    dim_type, place_name, place_df, uploaded, count_col, dim_col, should_extract=False
):

    place_df = convert_df(
        dim_type, place_df, place_name, "count", should_extract, dim_type
    )

    if dim_type == "week":
        uploaded["week"] = uploaded[dim_col].dt.weekday
        uploaded["week"] = uploaded["week"].replace(
            {0: "月曜", 1: "火曜", 2: "水曜", 3: "木曜", 4: "金曜", 5: "土曜", 6: "日曜"}
        )
    elif dim_type == "time":
        uploaded["time"] = uploaded[dim_col].dt.hour
    
    uploaded = convert_df(
        dim_type, uploaded, "アップロードされたデータ", count_col, should_extract, dim_col
    )

    df = pd.concat([place_df, uploaded], axis=0)

    return df
