from prometheus_client import start_http_server, Counter
import time
import os
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bleach

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://" + os.environ.get('GUESTBOOK_DB_ADDR')
mongo = PyMongo(app)

# Prometheus metric for counting messages
MESSAGE_COUNT = Counter('message_count_total', 'Total number of messages')

@app.route('/messages', methods=['GET'])
def get_messages():
    """ retrieve and return the list of messages on GET request """
    field_mask = {'author': 1, 'message': 1, 'date': 1, '_id': 0}
    msg_list = list(mongo.db.messages.find({}, field_mask).sort("_id", -1))
    MESSAGE_COUNT.inc(len(msg_list))  # Increment counter on each message request
    return jsonify(msg_list), 201

@app.route('/messages', methods=['POST'])
def add_message():
    """ save a new message on POST request """
    raw_data = request.get_json()
    msg_data = {'author': bleach.clean(raw_data['author']),
                'message': bleach.clean(raw_data['message']),
                'date': time.time()}
    mongo.db.messages.insert_one(msg_data)
    MESSAGE_COUNT.inc(1)  # Increment counter on each new message
    return jsonify({}), 201

if __name__ == '__main__':
    for v in ['PORT', 'GUESTBOOK_DB_ADDR']:
        if os.environ.get(v) is None:
            print("error: {} environment variable not set".format(v))
            exit(1)

    # Start Prometheus metrics server on port 8001
    start_http_server(8000)
    
    # Start Flask server for backend API
    app.run(debug=False, port=os.environ.get('PORT'), host='0.0.0.0')

