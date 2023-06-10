from flask import Flask

from analyze import analyze

app = Flask(__name__)


@app.route("/analitics/<int:company_id>")
def analyze_router(company_id):
    json_result = analyze(company_id)
    return json_result


if __name__ == '__main__':
    app.run()
