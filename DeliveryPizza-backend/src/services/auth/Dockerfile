FROM python:3.12

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv pip install --system .

CMD ["uvicorn", "services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8001"]