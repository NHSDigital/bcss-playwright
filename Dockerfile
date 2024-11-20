FROM python:3.12-slim

WORKDIR /test

# Install dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps
RUN playwright install chrome --with-deps

RUN mkdir -p /tests/
COPY ./tests/ ./tests/
RUN mkdir -p /utils/
COPY ./utils/ ./utils/
RUN mkdir -p /pages/
COPY ./pages ./pages
COPY ./pytest.ini ./pytest.ini
COPY ./run_tests.sh ./run_tests.sh
COPY ./.env ./.env

RUN chmod +x ./run_tests.sh
CMD bash run_tests.sh