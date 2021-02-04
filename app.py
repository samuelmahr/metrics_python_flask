import time

from flask import Flask, jsonify, request

app = Flask(__name__)

metrics = {}
seconds_per_hour = 3600


@app.route('/metric/<key>', methods=['POST'])
def save_metric(key):
    request_time = time.time()
    expire_time = request_time + seconds_per_hour

    # force json for this test example.
    request_body = request.get_json(force=True)

    # metrics array should be in asc order based on time
    # tough to decide whether or not to keep list updated here or at sum
    # if no metrics stored, create new metric with list of 1 obejct
    if not metrics.get(key):
        metrics.update({
            key: [
                {
                    'value': request_body['value'],
                    'expire_time': expire_time
                }
            ]
        })
    else:
        # expire old records
        # keep records up to date here and at sum to optimize performance for both
        # assuming there's a consistent volume of requests through here, the expiration should be quick
        latest_metrics = list()
        for metric in metrics[key]:
            if metric['expire_time'] > request_time:
                latest_metrics.append(metric)
            else:
                # short circuit, the rest of list should not be expired
                break

        latest_metrics.append(
            {
                'value': request_body['value'],
                'expire_time': expire_time
            }
        )

        # set metrics to metrics that are not expired
        metrics[key] = latest_metrics

    # normally i would echo the new object created
    return jsonify({}), 200


@app.route('/metric/<key>/sum', methods=['GET'])
def get_sum(key):
    request_time = time.time()
    if not metrics.get(key):
        return jsonify({}), 404

    latest_metrics = list()

    metric_sum = 0
    for metric in metrics[key]:
        if metric['expire_time'] > request_time:
            latest_metrics.append(metric)
            metric_sum = int(round(metric_sum + metric['value']))

    # set new list without expired records
    metrics[key] = latest_metrics
    return jsonify({"value": metric_sum}), 200


# in general if i had a scheduled job, i would expire records with a cron job
# or if we were querying a db, it would only query the last hour
if __name__ == '__main__':
    app.run()
