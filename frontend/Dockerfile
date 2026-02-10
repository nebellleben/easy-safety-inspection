FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application with Vite explicitly using the API URL
ARG VITE_API_URL=https://safety-backend-production.up.railway.app
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage: serve with nginx
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx config template (directory first)
RUN mkdir -p /etc/nginx/templates && \
echo 'server { \
    listen $PORT; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript; \
}' > /etc/nginx/templates/default.conf.template

ENV PORT=80
EXPOSE 80

# nginx will auto-expand templates in /etc/nginx/templates/
CMD ["nginx", "-g", "daemon off;"]
