# run_both.py

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# import app1
from server import create_app as create_app1
main_app = create_app1()

# import app2
from server_adm import create_app as create_app2
adm_app = create_app2()

# import app2
from server_regis import create_app as create_app3
regis_app = create_app3()

# merge
app = DispatcherMiddleware(
    main_app, { '/admin': adm_app, '/regis': regis_app }
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