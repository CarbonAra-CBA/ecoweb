from flask import (
    Blueprint, render_template,json, request
)

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/', method=['GET','POST'])
def home():
    if request.method == 'POST':
        print("Calculate Carbonfootprint")

    if request.method == 'GET':
        print("Home Page")

        return render_template('index.html')
