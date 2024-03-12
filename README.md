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
