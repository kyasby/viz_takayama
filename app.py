import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from apps import day, time, week, summary, summary_graph
from multiapp import MultiApp

app = MultiApp()

import os
import glob

st.title(glob.glob('./data/pic/*'))

print('getcwd:      ', os.getcwd())
print('__file__:    ', __file__)
st.title(os.getcwd())

# Add all your application here
app.add_app('かんたんな概要', summary.app)
app.add_app("日付の推移(多い日を確認する)", day.app)
app.add_app("曜日の推移（多い曜日を確認する）", week.app)
app.add_app("時間の推移（多い時間を確認する）", time.app)


#  タイトル画像
# img = Image.open("./data/zoom.png")
# st.image(img)

# The main app
app.run()


# mongoexport --port 27017 --db opendatacam --collection tracker --type json --out /data/db/917-21.json  \
# --query '{"timestamp": {"$gte":{"$date": "2021-09-17T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-09-22T00:00:00.000Z"}}}'
# --query '{"timestamp": {"$gte":{"$date": "2021-09-27T20:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-09-28T08:00:00.000Z"}}}'


# --query '{"timestamp": {"$gte":{"$date": "2021-09-27T00:00:00.000Z"}}, "timestamp": {"$lte": {"$date": "2021-10-11T00:00:00.000Z"}}}'