FROM python:3.9-slim
WORKDIR /app
COPY server.py .
COPY templates/ ./templates/
RUN pip install flask requests
CMD ["python", "server.py"]
