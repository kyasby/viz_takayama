from apps import newapp, app2 # import your app modules here
from multiapp import MultiApp


app = MultiApp()

# Add all your application here
app.add_app("new app", newapp.app)
app.add_app("app2", app2.app)


# The main app
app.run()