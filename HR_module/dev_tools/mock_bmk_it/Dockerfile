FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project

COPY dev_tools ./dev_tools

ENV PYTHONPATH=/app
EXPOSE 8088

CMD ["uv", "run", "uvicorn", "dev_tools.mock_bmk_it.main:app", "--host", "0.0.0.0", "--port", "8088"]
