# Build Stage
FROM node:22-alpine as build-stage
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Production Stage
FROM nginx:alpine

# Install netcat for connectivity checking
RUN apk add --no-cache netcat-openbsd

COPY nginx/nginx.prod.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Add wait script to default nginx entrypoint hooks
#COPY nginx/wait-for.sh /docker-entrypoint.d/99-wait-for.sh
#RUN chmod +x /docker-entrypoint.d/99-wait-for.sh
