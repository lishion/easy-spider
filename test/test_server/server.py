from flask import Flask, render_template, request, make_response
from uuid import uuid4
from time import sleep
from random import normalvariate
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


@app.route("/test_crawl/<p>", methods=['GET'])
def test_crawl(p):
    tags = []
    for i in range(10):
        d = uuid4()
        tags.append('<a href="{}">{}</a>'.format(d, d))
    delay_times = abs(normalvariate(0, 20))
    p == "start" or sleep(delay_times)
    print(p, delay_times)
    return """
    <html>
        <title>{}</title>
        <body>
        {}
        </body>
    </html>
    """.format(p , "\n".join(tags))


if __name__ == "__main__":
    app.run(debug=True)
