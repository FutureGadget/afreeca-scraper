FROM python:3.8.12-bullseye
WORKDIR /afreeca-scraper
COPY src/ src/

COPY requirements.txt .
COPY banner.txt .
RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]
