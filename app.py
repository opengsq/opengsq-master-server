from flask import Flask, abort, request, jsonify

from MasterServer import MasterServer

from BeamMP import BeamMP
from Factorio import Factorio
from Palworld import Palworld

app = Flask(__name__)


def search(args: dict, master_server: MasterServer):
    host = args.get('host')
    port = args.get('port')

    # Check if host and port are provided
    if not host or not port:
        abort(400, description="Missing parameters: 'host' and 'port' are required.")

    try:
        port = int(port)
    except ValueError:
        abort(400, description="'port' must be an integer.")

    result = master_server.find(host=host, port=port)

    # Check if result is found
    if not result:
        abort(404, description="No result found.")

    return jsonify(result)


@app.route('/beammp/search', methods=['GET'])
def beammp_search():
    return search(request.args, BeamMP())


@app.route('/factorio/search', methods=['GET'])
def factorio_search():
    return search(request.args, Factorio())


@app.route('/palworld/search', methods=['GET'])
def palworld_search():
    return search(request.args, Palworld())


if __name__ == '__main__':
    app.run(debug=True)
