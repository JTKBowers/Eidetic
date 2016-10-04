import os
import json
import random
import hashlib
import string

import flask

import db

app = flask.Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(
    DATABASE="dbname=eidetic user=eidetic",
))
app.config.from_envvar('EIDETIC_SETTINGS', silent=True)

from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(flask.g, 'psql_db'):
        flask.g.psql_db = db.DatabaseConnection(app.config['DATABASE'])
    return flask.g.psql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(flask.g, 'psql_db'):
        flask.g.psql_db.close()

# GET /metrics/
@app.route("/metrics/")
def get_metrics():
    '''
    Returns a list of available metrics.
    '''
    db = get_db()
    names = db.get_metrics()
    return_dict = {
        "metrics": [{"name": name} for name in names]
    }
    return json.dumps(return_dict)

def generate_key():
    '''
    Generates an API key - a 32 character random string composed of numbers and lowercase letters.
    '''
    key_length = 32
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(key_length))

# POST /add-metric?name=[name]
@app.route('/add-metric', methods=['POST'])
def add_metric():
    '''
    Adds a new metric. Returns the api key to be used to submit that metric.
    '''
    name = flask.request.args.get('name', None)
    if name is None:
        flask.abort(400)

    api_key = generate_key()
    key_hash = hashlib.sha512(api_key.encode('utf-8')).hexdigest()

    db = get_db()
    db.add_metric(name, key_hash)
    return json.dumps({"api_key": api_key})


# GET /metrics/[metric name]
# POST /metrics/[metric name]/?api_key=[API key]
@app.route('/metrics/<metric_name>', methods=['GET', 'POST'])
def metrics(metric_name):
    '''
    Adds a new reading to a metric's data, or retreives a subset of that metric's data.
    '''
    db = get_db()
    if flask.request.method == 'POST':
        api_key = flask.request.args.get('api_key', None)
        if api_key is None:
            flask.abort(403)
        key_hash = hashlib.sha512(api_key.encode('utf-8')).hexdigest()
        if key_hash != db.get_api_key_hash(metric_name):
            flask.abort(403)
        payload = flask.request.get_json()
        if "creation_time" not in payload:
            flask.abort(400)
        if "data" not in payload:
            flask.abort(400)
        creation_time = payload['creation_time']
        data = payload['data']
        db.insert_reading(metric_name, creation_time, json.dumps(data))
        return json.dumps({"success": "true"})
    elif flask.request.method == 'GET':
        readings = db.get_readings(metric_name)
        return_dict = {
            "metric_name": metric_name,
            "readings": [
                {"creation_time": creation_time, "data": data} for data, creation_time in readings
            ]
        }
        return json.dumps(return_dict, default=json_serial)

application = app
if __name__ == "__main__":
    app.run(debug=True)
