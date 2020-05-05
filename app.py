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
        season, show, items = main(query)
        return jsonify({"query":query, "season":season, "title":show.title, "items":[i.dict() for i in items]})
    except Exception as e:
        return jsonify({"query":query, "error":str(e)})

if __name__=='__main__':
    app.run(debug=True)
