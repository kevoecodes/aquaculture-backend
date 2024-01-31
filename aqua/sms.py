import json
import requests

from aquaculture_backend.settings import SMS_API_KEY, SMS_SECRET_KEY


def send_sms(cellphone, message):
    url = 'https://apisms.beem.africa/v1/send'
    api_key = SMS_API_KEY
    secret_key = SMS_SECRET_KEY
    content_type = 'application/json'
    source_addr = 'INFO'
    message = message

    payload = {
        "source_addr": source_addr,
        "schedule_time": "",
        "encoding": 0,
        "message": message,
        "recipients": [
            {
                "recipient_id": 1,
                "dest_addr": str(cellphone),
            },
        ],
    }
    try:
        with requests.post(url=url, data=json.dumps(payload),
                           headers={'Content-Type': content_type,
                                    'Authorization': 'Basic ' + api_key + ':' + secret_key, },
                           auth=(api_key, secret_key), verify=True) as r:
            r_json = r.json()
            # dumps the json object into an element
            json_str = json.dumps(r_json)
            # load the json to a string
            response = json.loads(json_str)
            print("Response", response)
    except requests.exceptions.Timeout as e:
        print("Please check connection and try again.", e)
    except requests.exceptions.TooManyRedirects as er:
        print("Please check connection and try again.", er)
    except requests.exceptions.RequestException as err:
        print("System error contact administrator!", err)
    else:
        return response
