# Stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Copier package files
COPY package*.json ./

# Installer dépendances
RUN npm ci

# Copier source
COPY . .

# Build arguments pour variables d'env (injectées à build time par Railway)
ARG VITE_API_URL
ARG VITE_API_KEY

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_KEY=$VITE_API_KEY

# Build
RUN npm run build

# Stage production
FROM node:18-alpine

WORKDIR /app

# Installer serve
RUN npm install -g serve

# Copier le build
COPY --from=builder /app/dist ./dist

# Exposer port (Railway injecte PORT au runtime)
EXPOSE 3000

# Lancer serve (port dynamique pour Railway)
CMD ["sh", "-c", "serve -s dist -l ${PORT:-3000}"]
