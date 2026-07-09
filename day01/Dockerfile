FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir ollama fpdf2
COPY main.py .
CMD ["python", "main.py"]