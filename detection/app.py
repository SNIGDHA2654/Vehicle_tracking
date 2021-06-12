from flask import Flask, request, render_template, redirect
from flask.wrappers import Response
from flask_restful import reqparse
import os

from main import capture

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        in_file = request.files['upload']
        if request.files['upload'].filename == '':
            return redirect(request.host_url)
        in_file.save(in_file.filename)
        data = Response.get_json(capture(in_file.filename))
        os.remove(in_file.filename)

        return render_template('output.html', data = data)
    else:
        return render_template("base.html")

if __name__ == '__main__':
    app.run(debug=True)