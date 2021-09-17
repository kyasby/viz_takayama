from apps import newapp, app2
from multiapp import MultiApp


app = MultiApp()

# Add all your application here
app.add_app("月別データ", newapp.app)
app.add_app("app2", app2.app)


# The main app
app.run()