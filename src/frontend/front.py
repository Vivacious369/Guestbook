import json
import os
import datetime
import time
from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
import dateutil.relativedelta
from prometheus_client import start_http_server, Counter, generate_latest  # Import Prometheus client

app = Flask(__name__)

# Prometheus metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method'])

app.config["BACKEND_URI"] = 'http://{}/messages'.format(os.environ.get('GUESTBOOK_API_ADDR'))

@app.route('/')
def main():
    """ Retrieve a list of messages from the backend, and use them to render the HTML template """
    response = requests.get(app.config["BACKEND_URI"], timeout=3)
    json_response = json.loads(response.text)
    REQUESTS.labels(method='GET').inc()  # Increment counter for GET requests
    return render_template('home.html', messages=json_response)

@app.route('/post', methods=['POST'])
def post():
    """ Send the new message to the backend and redirect to the homepage """
    new_message = {'author': request.form['name'],
                   'message':  request.form['message']}
    requests.post(url=app.config["BACKEND_URI"],
                  data=jsonify(new_message).data,
                  headers={'content-type': 'application/json'},
                  timeout=3)
    return redirect(url_for('main'))

@app.route('/metrics')
def metrics():
    """Expose metrics to Prometheus"""
    return generate_latest(REQUESTS)  # Returns the metrics in the correct format

def format_duration(timestamp):
    """ Format the time since the input timestamp in a human readable way """
    now = datetime.datetime.fromtimestamp(time.time())
    prev = datetime.datetime.fromtimestamp(timestamp)
    rd = dateutil.relativedelta.relativedelta(now, prev)

    for n, unit in [(rd.years, "year"), (rd.days, "day"), (rd.hours, "hour"),
                    (rd.minutes, "minute")]:
        if n == 1:
            return "{} {} ago".format(n, unit)
        elif n > 1:
            return "{} {}s ago".format(n, unit)
    return "just now"


if __name__ == '__main__':
    for v in ['PORT', 'GUESTBOOK_API_ADDR']:
        if os.environ.get(v) is None:
            print("error: {} environment variable not set".format(v))
            exit(1)

    # Register format_duration for use in HTML template
    app.jinja_env.globals.update(format_duration=format_duration)

    # Start Prometheus metrics server
    start_http_server(8000)  # Prometheus will scrape metrics from this port

    # Start Flask app
    app.run(debug=False, port=os.environ.get('PORT'), host='0.0.0.0')
