FROM python:3.12

WORKDIR /app

COPY pyproject.toml .

RUN pip install uv
RUN uv pip install --system .

COPY . .

CMD ["uvicorn", "services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8001"]