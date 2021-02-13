from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        print(request.form)
        return request.form
    else:
        return 'GET not implemented'


if __name__ == '__main__':
    app.run()