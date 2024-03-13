import os
from flask import Flask, abort, request, jsonify
from flasgger import Swagger
import flask_monitoringdashboard as dashboard

import markdown

from config import build_config_file
from protocols import MasterServer, BeamMP, Factorio, Palworld, Scum
from version import __version__

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', '')

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "title": "OpenGSQ Master Server Search API",
    "version": __version__,
    "description": "Powered By OpenGSQ",
    "termsOfService": "/terms",
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/",
    "favicon": "/static/favicon.ico"
}
swagger = Swagger(app, config=swagger_config)


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
    """
    BeamMP Search
    This endpoint allows you to search for a BeamMP server using its host and port.
    ---
    tags:
      - Search EndPoint
    parameters:
      - name: host
        in: query
        type: string
        required: true
      - name: port
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Success
      400:
        description: Invalid parameters were supplied. 'host' and 'port' must be provided, and 'port' must be an integer.
      404:
        description: No server was found with the provided host and port.
    """
    return search(request.args, BeamMP())


@app.route('/factorio/search', methods=['GET'])
def factorio_search():
    """
    Factorio Search
    This endpoint allows you to search for a Factorio server using its host and port.
    ---
    tags:
      - Search EndPoint
    parameters:
      - name: host
        in: query
        type: string
        required: true
      - name: port
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Success
      400:
        description: Invalid parameters were supplied. 'host' and 'port' must be provided, and 'port' must be an integer.
      404:
        description: No server was found with the provided host and port.
    """
    return search(request.args, Factorio())


@app.route('/palworld/search', methods=['GET'])
def palworld_search():
    """
    Palworld Search
    This endpoint allows you to search for a Palworld server using its host and port.
    ---
    tags:
      - Search EndPoint
    parameters:
      - name: host
        in: query
        type: string
        required: true
      - name: port
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Success
      400:
        description: Invalid parameters were supplied. 'host' and 'port' must be provided, and 'port' must be an integer.
      404:
        description: No server was found with the provided host and port.
    """
    return search(request.args, Palworld())


@app.route('/scum/search', methods=['GET'])
def scum_search():
    """
    SCUM Search
    This endpoint allows you to search for a SCUM server using its host and port.
    ---
    tags:
      - Search EndPoint
    parameters:
      - name: host
        in: query
        type: string
        required: true
      - name: port
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Success
      400:
        description: Invalid parameters were supplied. 'host' and 'port' must be provided, and 'port' must be an integer.
      404:
        description: No server was found with the provided host and port.
    """
    return search(request.args, Scum())


@app.route("/terms")
def render_terms():
    # Read the contents of terms.md
    with open("terms.md", "r") as terms_file:
        md_content = terms_file.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)

    return html_content


@app.route("/stats")
def render_stats():
    """
    Statistics Requests
    This endpoint allows you to retrieve the count of servers for each server type.
    ---
    tags:
      - Statistics Endpoint
    responses:
      200:
        description: Success
    """
    db = MasterServer.get_db()

    # Get a list of collection names in the database
    collection_names = db.list_collection_names()

    # Create a dictionary to store collection counts
    collection_counts = {
        name.lower(): db[name].count_documents({}) for name in collection_names}

    return collection_counts


build_config_file()
dashboard.config.init_from(file='config.cfg')
dashboard.bind(app)

if __name__ == '__main__':
    app.run(debug=True)
