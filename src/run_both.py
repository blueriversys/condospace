# run_both.py

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# import app1
from server import create_app as app_1_create_app
app1 = app_1_create_app()

# import app2
from server_adm import create_app as app_2_create_app
app2 = app_2_create_app()

# merge
app = DispatcherMiddleware(
    app1, { '/admin': app2 }
)

# run_simple() is only invoked when run_both.py is run from the command-line, like this:
# python run_both.py
# In the container server, it runs through GUNICORN, which takes the "app" variable (see Dockerfile)
if __name__ == '__main__':
    run_simple(
        hostname='0.0.0.0',
        port=5000,
        application=app,
        use_reloader=True,
        use_debugger=False,
        use_evalex=True)