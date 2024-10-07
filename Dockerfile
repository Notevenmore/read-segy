FROM python:3.9-alpine3.20
COPY requirements.txt ./read-segy
WORKDIR /read-segy
RUN python -m venv venv && \
  ./venv/bin/pip install --upgrade pip && \
  ./venv/bin/pip install -r requirements.txt
COPY . .
EXPOSE 3001
CMD ["./venv/bin/python", "app.py"]