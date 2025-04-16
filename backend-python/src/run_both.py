# run_both.py

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# import app1
from server import create_app as create_app1

# import app2
from server_adm import create_app as create_app2

# import app3
from server_react import create_app as create_app3

app1 = create_app1()
app2 = create_app2()
app3 = create_app3()

# merge
app = DispatcherMiddleware(
    app1, { '/admin': app2, '/react': app3 }
)

print("here after creating the app variable")

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