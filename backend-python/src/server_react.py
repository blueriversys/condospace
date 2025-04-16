import time
from flask import Flask, send_from_directory, render_template

# the relative path, which takes the location of this server as the starting point
# The "dist" folder is created by the "npm run build" command, issued from the root folder of the front end: "frontend-react"
# The .html files in the "dist" folder are not used at all; .html are taken from the "templates" folder
app = Flask(__name__, static_folder='../../frontend-react/dist', template_folder='../../frontend-react/src/templates')

# @app.route('/js/<path:rel_path>')
# def common_static_images(rel_path):
#     print(f"in common_static_images(): rel_path: {rel_path}")
#     return send_from_directory('static', f"{rel_path}")
#
@app.route('/')
def index():
    print("here in server_react/index()")
    return render_template('index.html')

@app.route('/page1')
def page1():
    print("here in server_react/page1()")
    return render_template('page1.html')

@app.route('/page2')
def page2():
    print("here in server_react/page2()")
    return render_template('page2.html')

@app.route('/home')
def home():
    print("here in server_react/home()")
    #return app.send_static_file('index.html')
    return render_template('index.html')

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

def create_app():
    app_name = 'server_react.py'
    print(f"app name: {app_name}")
    return app

