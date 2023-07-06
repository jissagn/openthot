

FROM python:3.11-slim


ENV DOCKER_USER sous-titreur
ENV PATH /usr/src/sous-titreur/bin:/root/.local/bin/:$PATH
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1

RUN groupadd -r $DOCKER_USER && useradd -r -m -g $DOCKER_USER $DOCKER_USER

RUN mkdir -p /usr/src/sous-titreur
WORKDIR /usr/src/sous-titreur

RUN set -ex \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    htop \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -
RUN poetry config virtualenvs.create false

# Deal with python requirements
COPY pyproject.toml /usr/src/sous-titreur/
# COPY poetry.lock /usr/src/sous-titreur/
RUN poetry lock
RUN poetry install --only main --no-root

RUN pip install git+https://github.com/m-bain/whisperx.git 

# Copy the remaining sources
COPY . /usr/src/sous-titreur/

EXPOSE 8000

CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "stt.api.main:app"]
