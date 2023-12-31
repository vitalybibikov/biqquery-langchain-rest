# Stage 1: Build stage
FROM python:3.11-slim-buster AS builder

WORKDIR /app
ADD . /app

RUN touch output.log

RUN apt-get update && \
    apt-get install -y build-essential

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim-buster

WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /install /usr/local

RUN apt-get update && \
    apt-get install -y nginx

COPY nginx.conf /etc/nginx/nginx.conf

# Set default values for environment variables
ENV SERVICE_ACCOUNT_FILE="./service-account-key.json"
ENV TOP_K="1000"
ENV DEBUG="True"
ENV TIMEOUT="300"
ENV NGINX_SERVER_NAME="localhost"
ENV LANGCHAIN_VERBOSE="True"

# # Turns off buffering for easier container logging
# ENV PYTHONUNBUFFERED=1 
# ENV PYTHONDONTWRITEBYTECODE=1

#CMD nginx && python app/main.py
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]
CMD nginx && gunicorn -b 0.0.0.0:5000 app.main:app --timeout $TIMEOUT

