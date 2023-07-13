

FROM python:3.11-slim

ARG ASR__ENGINE

ENV DOCKER_USER openthot
ENV PATH /usr/src/openthot/bin:/root/.local/bin/:$PATH
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1

RUN groupadd -r $DOCKER_USER && useradd -r -m -g $DOCKER_USER $DOCKER_USER

RUN mkdir -p /usr/src/openthot
WORKDIR /usr/src/openthot

RUN set -ex \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    llvm-dev \
    htop \
    sudo \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -
RUN poetry config virtualenvs.create false

# Deal with python requirements
COPY pyproject.toml /usr/src/openthot/
# COPY poetry.lock /usr/src/openthot/
RUN poetry lock

RUN poetry install --only main --only $ASR__ENGINE --sync


# Copy the remaining sources
COPY . /usr/src/openthot/

EXPOSE 8000

CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "openthot.api.main:app"]
