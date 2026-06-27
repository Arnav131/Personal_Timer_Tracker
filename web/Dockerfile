# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app

ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_PUBLISHABLE_KEY=$VITE_SUPABASE_PUBLISHABLE_KEY

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm test && npm run build

# GitHub Actions exports this stage and sends the static files to Netlify.
FROM scratch AS export
COPY --from=build /app/dist /

# Optional local production container: docker build -t productivity-enforcer ./web
FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
