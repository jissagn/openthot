
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

**OpenThot** API is a **python FastAPI** that provides an interviews transcription tool, by standing on the shoulders of existing open-source ASR engines that also provide diarization (currently [whisperX](https://github.com/jissagn/openthot) and [wordcab-transcribe](https://github.com/Wordcab/wordcab-transcribe), feel free to contribute with yours 😉).

It basically adds a stateful layer so you can compute, store, view and modify the results in a unified way.

It can be combined with a frontend (such as [**OpenThot** frontend](http://)).

## Setup

Copy the default `.env` and `secrets.env` files

```bash
cp .env.example .env
cp secrets.env.example secrets.env
```

and modify them with your own credentials if needed (e.g. the HuggingFace token if you plan to use [whisperX]() as ASR.)

## Docker commands

Build the image.

```bash
docker build -t openthot_api:latest .
```

Run the container.

```bash
docker run -d --name openthot_api \
    -p 8000:8000 \
    --env-file .env \
    --env-file secrets.env \
    -v ./data:/usr/src/openthot/data \
    openthot_api:latest
```
