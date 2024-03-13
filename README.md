# OpenGSQ Master Server Search API

[![Docker Image CI](https://github.com/opengsq/opengsq-master-server/actions/workflows/docker-image.yml/badge.svg)](https://github.com/opengsq/opengsq-master-server/actions/workflows/docker-image.yml)
[![GitHub license](https://img.shields.io/github/license/opengsq/opengsq-master-server)](https://github.com/opengsq/opengsq-master-server/blob/main/LICENSE)

This is an application that provides an API for searching game servers. The application supports the following games: BeamMP, Factorio, Palworld, and Scum.

Try now: https://master-server.opengsq.com

## Usage

The application provides the following endpoints:

- `/beammp/search?host=<host>&port=<port>`
- `/factorio/search?host=<host>&port=<port>`
- `/palworld/search?host=<host>&port=<port>`
- `/scum/search?host=<host>&port=<port>`

Replace `<host>` and `<port>` with the host and port of the game server you want to search.

## Error Handling

The application will return a 400 error if the 'host' and 'port' parameters are not provided or if the 'port' parameter is not an integer. If no result is found, the application will return a 404 error.

## License

This project is licensed under the MIT License.

## Stargazers over time

[![Stargazers over time](https://starchart.cc/opengsq/opengsq-master-server.svg?variant=adaptive)](https://starchart.cc/opengsq/opengsq-master-server)

---

## Development Setup

Follow these steps to set up your development environment:

1. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
2. Activate the virtual environment:
    - On Windows, run: `venv\Scripts\activate`
    - On Unix or MacOS, run: `source venv/bin/activate`
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Copy the `.env.example` file to a new file named `.env` and update the variables as needed:

```bash
cp .env.example .env
```

Here's what each variable in the `.env` file represents:

- `DATABASE_URL`: The URL of your mongodb database.
- `PORT`: The port number on which the Flask application will run.
- `FACTORIO_USERNAME`: Your Factorio username.
- `FACTORIO_TOKEN`: Your Factorio token.
- `USERNAME`: The username for the Flask-MonitoringDashboard.
- `PASSWORD`: The password for the Flask-MonitoringDashboard.
- `SECURITY_TOKEN`: The security token for the Flask-MonitoringDashboard.

## Running the Application

You can start the scheduled task or run the Flask application in debug mode:

- Start the scheduled task:
    ```bash
    python main.py
    ```
- Run Flask in debug mode:
    ```bash
    python app.py
    ```
- Run Protocol:
    ```bash
    python -m protocol.BeamMP
    ```

## Self-Hosting

You can use Docker Compose to self-host the application. Here's how:

1. Ensure that you have the following file structure:
    - `docker-compose.yml`
    - `.env`

2. Create a `docker-compose.yml` file with the following content:

    ```yml
    version: '3.8'
    services:
      flask:
        image: opengsq/opengsq-master-server:latest
        command: gunicorn -w 4 -b :8000 app:app
        container_name: opengsq-master-server-flask
        environment:
          - FLASK_ENV=production
        env_file:
          - .env
        ports:
          - ${PORT}:8000
        restart: always
        volumes:
          - ./data:/app/data

      schedule:
        image: opengsq/opengsq-master-server:latest
        command: python main.py
        container_name: opengsq-master-server-schedule
        env_file:
          - .env
        restart: always
    ```

3. Create a `.env` file as stated in the Configuration section.

4. Run the following command to start the application:

    ```bash
    docker-compose up -d
    ```
