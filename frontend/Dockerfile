FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY ./frontend/public ./public
COPY ./frontend/src ./src
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

