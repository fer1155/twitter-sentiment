# Etapa 1: construir la app con Vite
FROM node:18-alpine as build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Etapa 2: servir con Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
