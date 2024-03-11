from flask import Flask, abort, request, jsonify
from Palworld import Palworld

app = Flask(__name__)


@app.route('/palworld/search', methods=['GET'])
def palworld_search():
    host = request.args.get('host')
    port = request.args.get('port')

    # Check if host and port are provided
    if not host or not port:
        abort(400, description="Missing parameters: 'host' and 'port' are required.")

    try:
        port = int(port)
    except ValueError:
        abort(400, description="'port' must be an integer.")

    result = Palworld().find(host=host, port=port)

    # Check if result is found
    if not result:
        abort(404, description="No result found.")

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
