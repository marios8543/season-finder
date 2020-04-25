from flask import Flask, render_template, jsonify, request
from seasons import main

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("help.html")

@app.route("/season", methods=["POST"])
def season():
    query = request.form.get("query")
    if not query:
        return jsonify({"error":"No query passed"})
    try:
        return jsonify({"query":query, "season":main(query)})
    except Exception as e:
        return jsonify({"query":query, "error":e})

if __name__=='__main__':
    app.run(debug=True)