from flask import Flask, render_template, request, jsonify
import json
import math

app = Flask(__name__)


@app.route("/")
def index():
    with open("all_streamers_names.txt", "r", encoding="UTF-8") as file:
        names = [line.strip() for line in file.readlines()]

    with open("streamers.json", "r") as json_file:
        streamers_json = json.load(json_file)

    page = request.args.get("page", 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = math.ceil((len(names) + per_page - 1) / per_page)

    items_on_page = names[start:end]

    return render_template(
        "index.html",
        names=names,
        streamers_img=streamers_json,
        items_on_page=items_on_page,
        total_pages=total_pages,
        page=page,
    )


@app.route("/save_names", methods=["POST"])
def save_names():
    data = request.get_json()
    names = data.get("names", [])

    # Write names to a file (append if the file exists)
    with open("female_streamers.txt", "a", encoding="UTF-8") as file:
        for name in names:
            file.write(name + "\n")

    return jsonify({"message": "Names saved successfully"})


if __name__ == "__main__":
    app.run(debug=True)
