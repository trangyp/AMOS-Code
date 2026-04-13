# AMOS Brain Admin Dashboard
# Simple nginx server for static files

FROM nginx:alpine

# Copy dashboard files
COPY index.html /usr/share/nginx/html/
COPY *.js /usr/share/nginx/html/ 2>/dev/null || true
COPY *.css /usr/share/nginx/html/ 2>/dev/null || true

# Configure nginx
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
