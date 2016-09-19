import os
import json
import random
import hashlib
import string

import psycopg2

import flask
app = flask.Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(
    DATABASE="dbname=eidetic user=eidetic",
))
app.config.from_envvar('EIDETIC_SETTINGS', silent=True)

def db_connect():
    return psycopg2.connect(app.config['DATABASE'])

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(flask.g, 'psql_db'):
        flask.g.psql_db = db_connect()
    return flask.g.psql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(flask.g, 'psql_db'):
        flask.g.psql_db.close()

# GET /metrics/
@app.route("/metrics/")
def get_metrics():
    cur = get_db().cursor()
    cur.execute("SELECT name FROM metrics;")
    names = cur.fetchall()
    return_dict = {
        "metrics": [{"name": name} for name in names]
    }
    return json.dumps(return_dict)

def generate_key():
    key_length = 32
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(key_length))

# POST /add-metric?name=[name]
@app.route('/add-metric', methods=['POST'])
def add_metric():
    name = flask.request.args.get('name', None)
    if name is None:
        flask.abort(400)
    cur = get_db().cursor()
    api_key = generate_key()
    cur.execute(
        """INSERT INTO metrics (name, key_hash, privileged)
        VALUES (%s, %s, FALSE);""",
        (name, hashlib.sha512(api_key.encode('utf-8')).hexdigest())
    )
    return json.dumps({"api_key": api_key})


# GET /metrics/[metric name]
# POST /metrics/[metric name]/?api_key=[API key]
@app.route('/metrics/<metric_name>', methods=['GET', 'POST'])
def metrics(metric_name):
    if flask.request.method == 'POST':
        api_key = flask.request.args.get('api_key', None)
        if name is None:
            flask.abort(400)
    elif flask.request.method == 'GET':
        cur = get_db().cursor()
        cur.execute("SELECT data, creation_time FROM data WHERE metric_name = metric_name;")
        readings = cur.fetchall()
        return_dict = {
            "metric_name": metric_name,
            "readings": [
                {"creation_time": creation_time, "data": data} for data, creation_time in readings
            ]
        }
        return json.dumps(return_dict)

if __name__ == "__main__":
    app.run(debug=True)
