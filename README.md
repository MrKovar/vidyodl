# vidyodl

Host your own video downloading API! Built in homage to [pytube](https://github.com/pytube/pytube) but with an emphasis on privacy, utilizing Piped! Want to download a video from your favorite site, Piped? How about just the audio? How about an entire YouTube playlist? You came to the right repo! Using celery to create an efficient download queue, you can queue up as many downloads as you want and they will be processed in the order they were received and save them to a directory of your choosing.

## Getting Started

This is designed to run in a containerized environment. However, it can be run locally as well if you have the correct dependencies installed.

The API has a few main endpoints that you can use to download videos:

* `/download` - Download a single video

* `/download_playlist` - Download an entire playlist

* `/download_audio` - Download the audio from a video

Once the application has started, you can access the API at `http://localhost:8069/docs` for more information.

### Prerequisites

#### Containerized (Recommended)

You will need to have [Docker](https://docs.docker.com/get-docker/) installed on your system.

If you are unsure whether or not Docker is properly installed, Docker provides a [test image](https://hub.docker.com/_/hello-world) that you can run to verify that everything is working as expected.

#### Local

For local usage, you will need to have the following installed:

* Python 3.6+
* Poetry
* ffmpeg

### Installing (Only needed for local use)

Poetry is used to manage the dependencies for this project. To install the depndencies for this project, run the following command:

```shell
poetry install
```

## Running the tests

For simplicity, a Makefile command is provided to run the tests.

```shell
make test
```

if you wish to run the tests manually, you can do so with the following command:

```shell
pytest path/to/tests -k test_name
```

## Deployment


### Containerized Deployment (Recommended)

To run the application in a containerized environment, a compose file has been provided. To start the application, run the following command:

```shell
make build-and-start
```

### Local Deployment

To run the application locally, you will need to have a redis server running that Celery can connect to.

Then, you will need to start the Celery worker:

```shell
poetry run celery -A app.tasks.celery_app worker
```

Then you can start the API:

```shell
poetry run uvicorn server.main:vidyodl_app --port=8069
```

## Built With

* [FastAPI](https://fastapi.tiangolo.com/) - API Framework
* [Celery](https://docs.celeryproject.org/en/stable/) - Distributed Task Queue
* [Docker](https://www.docker.com/) - Containerization Platform

## Contributing

When raising a PR, please ensure that you have run the following commands when applicable:

```shell
make lint
make test
```

## Versioning

Project to use [SemVer](http://semver.org/) for versioning.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Huge thank you to the developers of [pytube](https://github.com/pytube/pytube) who inspired this project and provided a great starting point for the YouTube download functionality and Playlist parsing abilities.
* Thank you to the developers of [Piped](https://github.com/TeamPiped/Piped/tree/master) who created something really useful for people who may not want to have their information constantly scraped but still want to be able to use the services that they provide.
