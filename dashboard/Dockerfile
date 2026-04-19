# AMOS Dashboard - Frontend Dockerfile
# Multi-stage build for optimized production image
#
# Stage 1: Build React application
# Stage 2: Serve with Nginx
#
# Creator: Trang Phan
# Version: 3.0.0

# =================== STAGE 1: Build ===================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# =================== STAGE 2: Serve ===================
FROM nginx:alpine

# Install security updates
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy landing page
COPY --from=builder /app/public/landing.html /usr/share/nginx/html/landing.html

# Create health check endpoint
RUN echo '{"status":"healthy","service":"amos-frontend"}' > /usr/share/nginx/html/health

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
