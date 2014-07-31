from flask import Flask
app = Flask(__name__)

app.secret_key = "C0d3_Camp_13_aw3s0m3!x" # For sessions
app.config["UPLOAD_FOLDER"] = "piculiar/static/uploads"

import piculiar.routes

