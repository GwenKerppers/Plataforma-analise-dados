FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY pyproject.toml alembic.ini ./
COPY app ./app
COPY alembic ./alembic
COPY tests ./tests
RUN pip install --no-cache-dir -e ".[dev]"
RUN useradd --create-home appuser && chown -R appuser /srv
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
