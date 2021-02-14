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

locations = pd.read_csv(
    'https://github.com/reichlab/covid19-forecast-hub/raw/master/data-locations/locations.csv')
deaths = pd.read_csv(
    'https://github.com/hannanabdul55/covid19-forecast-hub/raw/master/data-truth/truth-Incident%20Deaths.csv').merge(
    locations, how='left', on=['location', 'location_name']).dropna(subset=['abbreviation'])

cases = pd.read_csv(
    'https://github.com/hannanabdul55/covid19-forecast-hub/raw/master/data-truth/truth-Incident%20Cases.csv').merge(
    locations, how='left', on=['location', 'location_name']).dropna(subset=['abbreviation'])
deaths['date'] = pd.to_datetime(deaths.date, infer_datetime_format=True)
cases['date'] = pd.to_datetime(cases.date, infer_datetime_format=True)

date_format = '%Y-%m-%d'
text_date_format = '%a %b %d %Y'


# deaths = deaths.merge(locations, how='left', on=['location', 'location_name'])
# cases = cases.merge(locations, how='left', on=['location', 'location_name'])


@app.route('/', methods=['GET', 'POST'])
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
        range = False
        if 'date-time' in req['queryResult']['parameters'] and req['queryResult']['parameters'][
            'date-time'] != '':
            date = parser.parse(req['queryResult']['parameters']['date-time'])
        elif 'endDate' in dates and 'startDate' in dates:
            range = True
            start_date = parser.parse(dates['startDate']).date()
            end_date = parser.parse(dates['endDate']).date()
        elif 'endDate' in dates:
            date = parser.parse(dates['endDate']).date()
        elif 'startDate' in dates:
            date = parser.parse(dates['startDate']).date()
        else:
            date = datetime.now().date()

        # intent_val = str(intent['displayName']).lower()
        val = -1
        if intent['displayName'] == "Deaths":
            if not range:
                val = deaths.loc[(deaths['location_name'] == state) & (
                            deaths['date'] == date.strftime(date_format))]['value'].sum()
            else:
                val = deaths.loc[(deaths['location_name'] == state) & (
                        deaths['date'] >= start_date.strftime(date_format)) & (
                                         deaths['date'] <= end_date.strftime(date_format))][
                    'value'].sum()
        if intent['displayName'] == "Cases":
            if not range:
                val = cases.loc[(cases['location_name'] == state) & (
                            cases['date'] == date.strftime('%Y-%m-%d'))]['value'].sum()
            else:
                val = cases.loc[(cases['location_name'] == state) & (
                        cases['date'] >= start_date.strftime(date_format)) & (
                                        cases['date'] <= end_date.strftime(date_format))][
                    'value'].sum()
            # val = cases.loc[(cases['location_name'] == state) & (cases['date'] == date.strftime('%Y-%m-%d'))]['value'].sum()
        if val == 0:
            final_resp = f"There were no {intent['displayName'].lower()} "
        else:
            final_resp = f"There were {val} {intent['displayName'].lower()} "
        if range is True:
            final_resp += f"from {start_date.strftime(text_date_format)} to {end_date.strftime(text_date_format)} "
        elif date is not None:
            final_resp += f"on {date.strftime(text_date_format)} "
        final_resp += f"in the state of {state}."
        return create_response_obj(final_resp)

    except KeyError as e:
        eprint("KeyError parsing response", e)
        return error_response
    # except:
    #     eprint("Unexpected error parsing response")
    #     return unexpected_error_response


if __name__ == '__main__':
    app.run()
