FROM python
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y software-properties-common && apt-get update && apt-add-repository non-free
RUN apt-get update && apt-get install -y unrar-free unrar
RUN pip install poetry
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-dev
COPY . /app
EXPOSE 8000