FROM python:3.14-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

# Copy dependency files first (layer caching)
COPY pyproject.toml .

# Install dependencies using UV (no venv, install straight to system)
RUN uv pip install --system --no-cache -r pyproject.toml

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
