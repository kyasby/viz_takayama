import time
import urllib.parse
from datetime import date

import pandas
import pandas as pd
import plotly.express as px
import streamlit as st
from statsmodels.tsa.seasonal import STL

OBJ_TYPE = ["person", "car", "bus", "truck", "bicycle", "motorbike"]


def show_title(url):
    place_name = urllib.parse.unquote(
        f'{url.split("/")[-1].split(".")[0].split("_")[-1]}'
    )
    st.title(place_name)

    return place_name


# 後から綺麗にする
# @st.experimental_memo
def load_date(dim_type, params):

    if params["place"] == "まるっとプラザ":
        pic_url = "/Users/ryo/Documents/Picture/高山/マルっと.png"
    else:
        pic_url = "./data/zoom.png"

    if dim_type == "day":
        if params["place"] == "まるっとプラザ":
            url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E3%81%BE%E3%82%8B%E3%81%A3%E3%81%A8%E3%83%97%E3%83%A9%E3%82%B6.csv"
            area = "plaza_car_near"
        else:
            url = "https://publickbacketmdg.s3.ap-northeast-1.amazonaws.com/day_grouped_by_%E6%9C%9B%E9%81%A0.csv"
            area = "juroku_zoom"
    elif dim_type == "week":
        if params["place"] == "まるっとプラザ":
            url = "/Users/ryo/Documents/Lab/Jetson/jetson_csv/9-3/week_grouped_by_まるっとプラザ.csv"
            area = "plaza_car_near"
        else:
            url = (
                "/Users/ryo/Documents/Lab/Jetson/jetson_csv/9-3/week_grouped_by_望遠.csv"
            )
            area = "juroku_zoom"
    elif dim_type == "time":
        if params["place"] == "まるっとプラザ":
            url = "/Users/ryo/Documents/Lab/Jetson/jetson_csv/10-21/time/plaza.csv"
            area = "plaza_right_far"
        else:
            url = "/Users/ryo/Documents/Lab/Jetson/jetson_csv/10-21/time/zoom.csv"
            area = "juroku_zoom"

    df = pd.read_csv(url)

    # カウント線を絞る TODO
    df = df[df["area"] == area]
    # 種類を絞る
    df = df[df["name"] == params["obj_type_selector"]]
    hol_edge = None
    if dim_type == "day":
        df.day = pd.to_datetime(df.day)

        df = (
            df.groupby(["day", "name", "area", "week", "is_holiday", "is_edge_holiday"])
            .sum()
            .reset_index()
        )

        df = df[
            (pd.to_datetime(params["date_start"]) <= df.day)
            & (df.day <= pd.to_datetime(params["date_end"]))
        ]

        # 休日の前後リスト
        hol_edge = df[df["is_edge_holiday"] == 1]["day"]
        hol_edge = sorted(hol_edge.unique())
    elif dim_type == 'week':
        df = df.groupby(['week', 'area', 'name']).mean().reset_index()
        
    elif dim_type == "time":
        df = df.groupby(["is_holiday", "time"]).mean().reset_index()
        df['is_holiday'] = df['is_holiday'].apply(lambda x: '休日' if x else '平日')

    return (
        pic_url,
        urllib.parse.unquote(f'{url.split("/")[-1].split(".")[0].split("_")[-1]}'),
        df,
        hol_edge,
    )


def set_params(is_map=False):
    global obj_type_selector, date_start, date_end, place

    if is_map:
        place = None
    else:
        place = st.sidebar.selectbox("場所を選んでください。", ["まるっとプラザ", "十六銀行高山支店"])

    obj_type_selector = st.sidebar.selectbox("Select your favorite flower", OBJ_TYPE)

    date_start = st.sidebar.date_input(
        "開始日",
        min_value=date(2021, 6, 26),
        max_value=date(2021, 9, 3),
        value=date(2021, 7, 1),
    )

    date_end = st.sidebar.date_input(
        "終了日",
        min_value=date(2021, 6, 26),
        max_value=date(2021, 9, 3),
        value=date(2021, 9, 3),
    )

    df = pd.DataFrame(
        {
            "English": [
                "January",
                "Feburary",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            "日本語": [
                "1月",
                "2月",
                "3月",
                "4月",
                "5月",
                "6月",
                "7月",
                "8月",
                "9月",
                "10月",
                "11月",
                "12月",
            ],
        }
    ).set_index("日本語")

    st.sidebar.table(df)

    params = {
        "obj_type_selector": obj_type_selector,
        "date_start": date_start,
        "date_end": date_end,
        "place": place,
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
            df["timestamp"] /= df["timestamp"].sum()

    elif dim_type == "week":
        df[dim_col] = df[dim_col].replace(
            {0: "月曜", 1: "火曜", 2: "水曜", 3: "木曜", 4: "金曜", 5: "土曜", 6: "日曜"}
        )

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
            lambda x: l_order.index(x) if x in l_order else -1
        )
        df = df.sort_values("order")

    elif dim_type == "time":
        pass

    df["type"] = place_name

    return df


@st.experimental_memo(suppress_st_warning=True)
def combine_df(
    dim_type, place_name, place_df, uploaded, count_col, dim_col, should_extract=False
):

    place_df = convert_df(
        dim_type, place_df, place_name, "timestamp", should_extract, dim_col
    )
    uploaded = convert_df(
        dim_type, uploaded, "アップロードされたデータ", count_col, should_extract, dim_col
    )

    df = pd.concat([place_df, uploaded], axis=0)

    return df
