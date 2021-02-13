from flask import Flask, request
import pandas as pd
import json
import sys

from datetime import datetime, date
from dateutil import parser
app = Flask(__name__)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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

error_response = {
  "fulfillmentMessages": [
    {
      "text": {
        "text": [
          "Something unexpected happened. Please try again"
        ]
      }
    }
  ]
}

def create_response_obj(resp_str):
    res = sample_response
    res['fulfillmentMessages'][0]['text']['text'] = [resp_str]
    return res

unexpected_error_response = {
  "fulfillmentMessages": [
    {
      "text": {
        "text": [
          "Error encountered. Please try again"
        ]
      }
    }
  ]
}

locations = pd.read_csv('https://github.com/reichlab/covid19-forecast-hub/raw/master/data-locations/locations.csv')
deaths = pd.read_csv('https://github.com/reichlab/covid19-forecast-hub/raw/master/data-truth/truth-Incident%20Deaths.csv').merge(locations, how='left', on=['location', 'location_name']).dropna(subset=['abbreviation'])

cases = pd.read_csv('https://github.com/reichlab/covid19-forecast-hub/raw/master/data-truth/truth-Incident%20Cases.csv').merge(locations, how='left', on=['location', 'location_name']).dropna(subset=['abbreviation'])
deaths['date'] = pd.to_datetime(deaths.date)
cases['date'] = pd.to_datetime(cases.date)



# deaths = deaths.merge(locations, how='left', on=['location', 'location_name'])
# cases = cases.merge(locations, how='left', on=['location', 'location_name'])


@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        return parse_response(data)
        return sample_response
    else:
        return 'GET not implemented'


def parse_response(req):
    try:
        intent = req['queryResult']['intent']
        state = req['queryResult']['parameters']["geo-state"]
        dates = req['queryResult']['parameters']['date-period']
        date = None
        if dates is None or dates == "":
            date = datetime.now().date()
        elif 'endDate' in dates:
            date = parser.parse(dates['endDate']).date()
        elif 'startDate' in dates:
            date = parser.parse(dates['startDate']).date()

        # intent_val = str(intent['displayName']).lower()
        val = -1
        if intent['displayName'] == "Deaths":
            val = deaths.loc[(deaths['location_name'] == state) & (deaths['date'] == date.strftime('%Y-%m-%d'))].iloc[0]['value']
        if intent['displayName'] == "Cases":
            val = cases.loc[(cases['location_name'] == state) & (cases['date'] == date.strftime('%Y-%m-%d'))].iloc[0]['value']
        return create_response_obj(f"The number of {intent} for {state} is {val}")



    except KeyError as e:
        eprint("KeyError parsing response", e)
        return error_response
    # except:
    #     eprint("Unexpected error parsing response")
    #     return unexpected_error_response



if __name__ == '__main__':
    app.run()