# OpenThot API

<!-- <a href="https://github.com/jissagn/openthot/actions?query=workflow%3Alint-and-test+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/jissagn/openthot/workflows/Lint%20and%20test/badge.svgevent=push&branch=main" alt="Test">
</a>
  <a href="https://github.com/jissagn/openthot/stargazers">
    <img src="https://img.shields.io/github/stars/jissagn/openthot.svg?colorA=orange&colorB=orange&logo=github"
         alt="GitHub stars">
  </a>
  <a href="https://github.com/jissagn/openthot/issues">
        <img src="https://img.shields.io/github/issues/jissagn/openthot.svg"
             alt="GitHub issues">
  </a>


</p> -->

## Description

**OpenThot** API is a **python FastAPI** that provides an interviews transcription tool, by standing on the shoulders of existing open-source ASR engines that also provide diarization (currently [whisperX](https://github.com/m-bain/whisperX) and [wordcab-transcribe](https://github.com/Wordcab/wordcab-transcribe), feel free to contribute with yours 😉).

It basically adds a stateful layer so you can compute, store, view and modify the results in a unified way.

It can be combined with a frontend (such as [**OpenThot** frontend](https://github.com/jissagn/openthot-front)).

## Setup

Copy the default `.env` and `secrets.env` files

```bash
cp .env.example .env
cp secrets.env.example secrets.env
```

and modify them with your own credentials if needed (e.g. the HuggingFace token if you plan to use [whisperX](https://github.com/m-bain/whisperX) as ASR.)


### Docker commands

First, load the .env file (we need the ASR\_\_ENGINE variable) :

```bash
source .env
```

Then build the image :

```bash
docker build --build-arg ASR__ENGINE=${ASR__ENGINE} -t openthot_api:${ASR__ENGINE} .
```

Run the api container :

```bash
docker run -d --name openthot_api \
    -p 8000:8000 \
    --env-file .env \
    --env-file secrets.env \
    -v ./data:/usr/src/openthot/data \
    openthot_api:${ASR__ENGINE}
```

Run the worker container :

```bash
docker run -d --name openthot_worker \
    --env-file .env \
    --env-file secrets.env \
    -v ./data:/usr/src/openthot/data \
    openthot_api:${ASR__ENGINE} \
    celery --app openthot.tasks.tasks.celery worker
```


### Run locally / contribute


#### 1. Requirements:

- poetry
- python 3.11 (you can use pyenv to handle python versions)
- direnv (optionnal)

#### 2. Setup

##### Virtual environment

Go to project folder, then :

- If `direnv` is installed : `direnv allow`.
- If not :
  ```bash
  poetry shell
  source .env
  ```

`direnv` takes care of loading/unloading the virtual env and the .env file whenever you enter/leave the project folder. If you don't use `direnv`, remember to run `poetry shell` and `source .env` each time you want to install/run the project.

##### Installation

```bash
poetry install --only main,cli,${ASR__ENGINE} --no-cache --sync
```

##### For contributors 🚀

```bash
pre-commit install

# note the additionnal `dev` group
poetry install --only main,cli,dev,${ASR__ENGINE} --no-cache --sync

pytest -m "not slow"  # discard the slowest tests
pytest  # run all tests
```

#### 3. Run

```bash
openthot --help
openthot standalone
```
