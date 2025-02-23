from prometheus_client import start_http_server, Counter, Histogram
import time
import os
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bleach

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://" + os.environ.get('GUESTBOOK_DB_ADDR')
mongo = PyMongo(app)

# Prometheus Metrics
MESSAGE_COUNT = Counter('message_count_total', 'Total number of messages')
REQUEST_COUNT = Counter('request_count_total', 'Total number of HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])
MONGODB_QUERY_DURATION = Histogram('mongodb_query_duration_seconds', 'MongoDB query execution time')
MONGODB_CONNECTION_ERRORS = Counter('mongodb_connection_errors_total', 'Total MongoDB connection errors')
MONGODB_INSERT_COUNT = Counter('mongodb_insert_count_total', 'Total number of inserted messages')

@app.route('/messages', methods=['GET'])
def get_messages():
    """Retrieve and return the list of messages on GET request."""
    start_time = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/messages').inc()
    
    try:
        field_mask = {'author': 1, 'message': 1, 'date': 1, '_id': 0}
        with MONGODB_QUERY_DURATION.time():  # Measure query time
            msg_list = list(mongo.db.messages.find({}, field_mask).sort("_id", -1))
        MESSAGE_COUNT.inc(len(msg_list))
        status_code = 200
    except Exception:
        MONGODB_CONNECTION_ERRORS.inc()
        status_code = 500
        msg_list = []

    REQUEST_DURATION.labels(method='GET', endpoint='/messages').observe(time.time() - start_time)
    return jsonify(msg_list), status_code

@app.route('/messages', methods=['POST'])
def add_message():
    """Save a new message on POST request."""
    start_time = time.time()
    REQUEST_COUNT.labels(method='POST', endpoint='/messages').inc()

    try:
        raw_data = request.get_json()
        msg_data = {'author': bleach.clean(raw_data['author']),
                    'message': bleach.clean(raw_data['message']),
                    'date': time.time()}
        with MONGODB_QUERY_DURATION.time():
            mongo.db.messages.insert_one(msg_data)
        MESSAGE_COUNT.inc(1)
        MONGODB_INSERT_COUNT.inc()
        status_code = 201
    except Exception:
        MONGODB_CONNECTION_ERRORS.inc()
        status_code = 500

    REQUEST_DURATION.labels(method='POST', endpoint='/messages').observe(time.time() - start_time)
    return jsonify({}), status_code

if __name__ == '__main__':
    for v in ['PORT', 'GUESTBOOK_DB_ADDR']:
        if os.environ.get(v) is None:
            print("error: {} environment variable not set".format(v))
            exit(1)

    # Start Prometheus metrics server on port 8001
    start_http_server(8000)
    
    # Start Flask server for backend API
    app.run(debug=False, port=os.environ.get('PORT'), host='0.0.0.0')
