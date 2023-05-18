# Stage 1
FROM node:14 as frontend_builder

WORKDIR /app/frontend

COPY frontend .

RUN npm install && npm install @popperjs/core && mkdir ../static && npm run build


# Stage 2
FROM python:3.9 as django_builder

WORKDIR /app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app

COPY --from=frontend_builder /app/static/bundle.js /app/static/bundle.js

RUN pip install --no-cache-dir -r requirements.txt && python manage.py collectstatic

