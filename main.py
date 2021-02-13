from flask import Flask, request

app = Flask(__name__)


@app.route('/', method='POST')
def hello_world():
    assert request.method == 'POST'
    print(request.form)
    return request.form


if __name__ == '__main__':
    app.run()