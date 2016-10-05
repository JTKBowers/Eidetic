import psycopg2

class DatabaseConnection:
    '''
    Provides an abstraction from the database.
    Exposes methods to connect & disconnect from a DB.
    It also provides high level methods to fetch data from the database.
    '''
    def __init__(self, host=None, port=None, dbname=None, dbuser=None, dbpass=None):
        conn_str = ''
        if host:
            conn_str += 'host=' + host
        if port:
            conn_str += ' port=' + port
        if dbname:
            conn_str += ' dbname=' + dbname
        if dbuser:
            conn_str += ' user=' + dbuser
        if dbpass:
            conn_str += ' password=' + dbpass
        self.db = psycopg2.connect(conn_str)
    def close(self):
        self.db.close()

    def get_metrics(self):
        '''
        Returns a list of available metrics.
        '''
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM metrics;")
        return cursor.fetchall()
    def add_metric(self, metric_name, metric_key_hash):
        '''
        Adds a new metric (not reading).
        Arguments:
            - metric_name: the name of the metric.
            - metric_key_hash: the SHA512 hash of the API key for this metric.
        Returns nothing.

        TODO: Error handling when the metric key hash is invalid.
        '''
        cursor = self.db.cursor()
        cursor.execute(
            """INSERT INTO metrics (name, key_hash, privileged)
            VALUES (%s, %s, FALSE);""",
            (metric_name, metric_key_hash)
        )
        self.db.commit()

    def get_readings(self, metric_name, limit=25):
        '''
        Retreives a list of readings for a metric.
        Arguments:
            - metric_name: the name of the metric to fetch.
            - limit: the maximum number of items to fetch (default 25). If it is None, they are all fetched.
        Returns a list of tuples of the form (data, creation_time).

        TODO: Error handling when the metric key hash is invalid.
        '''
        cursor = self.db.cursor()
        if limit is None:
            cursor.execute("SELECT data, creation_time FROM data WHERE metric_name = (%s) ORDER BY creation_time;", (metric_name,))
        else:
            cursor.execute("SELECT data, creation_time FROM data WHERE metric_name = (%s) ORDER BY creation_time LIMIT (%s);", (metric_name, limit))
        return cursor.fetchall()
    def insert_reading(self, metric_name, creation_time, data):
        '''
        Inserts a new reading.
        Arguments:
            - metric_name: the name of the metric.
            - creation_time: The creation time of the reading.
            - data: the JSON payload for the reading.
        Returns nothing.

        '''
        cursor = self.db.cursor()
        cursor.execute(
            """INSERT INTO data (metric_name, creation_time, insert_time, data)
            VALUES (%s, %s, now(), %s);""",
            (metric_name, creation_time, data)
        )
        self.db.commit()
    def get_api_key_hash(self, metric_name):
        '''
        Gets the API key hash for a metric.
        '''
        cursor = self.db.cursor()
        cursor.execute("SELECT key_hash FROM metrics WHERE name = (%s) LIMIT 1;", (metric_name,))
        return cursor.fetchone()[0]
