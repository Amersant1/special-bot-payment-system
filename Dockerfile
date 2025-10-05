FROM python:3.10-slim

WORKDIR /app

COPY payment_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY payment_service /app/payment_service

ENV PYTHONPATH=/app

EXPOSE 8082

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]


