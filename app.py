from apps import newapp, app2
from multiapp import MultiApp


app = MultiApp()

# Add all your application here
app.add_app("日付の推移(多い日を確認する)", newapp.app)
app.add_app("曜日の推移（多い曜日を確認する）", app2.app)


# The main app
app.run()