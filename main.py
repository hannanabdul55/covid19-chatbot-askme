from flask import Flask, request

app = Flask(__name__)

sample_response = {
  "fulfillmentMessages": [
    {
      "text": {
        "text": [
          "Sample response from the  covid webhook"
        ]
      }
    }
  ]
}

@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        print(request.data)
        return sample_response
    else:
        return 'GET not implemented'


if __name__ == '__main__':
    app.run()