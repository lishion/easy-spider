from flask import Flask, render_template, request, make_response

app = Flask(__name__, template_folder=".")


@app.route("/test_extract", methods=['GET'])
def test_extract():
    return render_template("./test_page.html")


@app.route("/test_encoding", methods=['GET'])
def test_encoding():
    charset = request.args.get("charset", "")
    response = make_response(render_template("./test_page.html"))
    response.content_type = f"text/html;charset={charset}"
    return response


if __name__ == "__main__":
    app.run(debug=True)
