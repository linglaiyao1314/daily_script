import json
from flask import Flask, jsonify

app = Flask(__name__)

with open("emoji_word.json") as f:
    DICT = json.load(f)


def emoji_transform(text, dictionary):
    return "".join([dictionary.get(i, i) for i in text])


@app.route("/<message>")
def index(message):
    try:
        data = emoji_transform(message, DICT)
    except Exception as e:
        return jsonify(status=0, data=emoji_transform("爷搞不定", DICT))
    return jsonify(data=data, status=1)


if __name__ == '__main__':
    app.run("0.0.0.0", port=8128)
