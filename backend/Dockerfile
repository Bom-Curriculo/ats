FROM node:22-alpine AS vite-build

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM php:8.4-cli

LABEL maintainer="servidor de tecnologia"

ENV TZ=America/Sao_Paulo

RUN apt-get update && apt-get install -y \
    $PHPIZE_DEPS \
    git \
    curl \
    unzip \
    zip \
    libzip-dev \
    libicu-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libonig-dev \
    libxml2-dev \
    libssl-dev \
    libpq-dev \
    libsqlite3-dev \
    && docker-php-ext-configure gd \
        --with-freetype \
        --with-jpeg \
    && docker-php-ext-install \
        bcmath \
        exif \
        gd \
        intl \
        opcache \
        pcntl \
        pdo_pgsql \
        pgsql \
        sockets \
        pdo_sqlite \
        zip \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    pecl channel-update pecl.php.net; \
    pecl clear-cache || true; \
    rm -rf /tmp/pear; \
    for attempt in 1 2 3; do \
        pecl install redis-6.3.0 && break; \
        if [ "$attempt" = "3" ]; then exit 1; fi; \
        pecl clear-cache || true; \
        rm -rf /tmp/pear; \
        sleep 3; \
    done; \
    docker-php-ext-enable redis; \
    php -m | grep -i '^redis$'; \
    rm -rf /tmp/pear

COPY --from=composer:2.8 /usr/bin/composer /usr/local/bin/composer

WORKDIR /var/www/html

COPY composer.json composer.lock ./

RUN composer install \
    --prefer-dist \
    --no-interaction \
    --no-progress \
    --no-scripts \
    --no-autoloader

COPY . .

COPY --from=vite-build /app/public/build /var/www/html/public/build

RUN composer dump-autoload --optimize \
    && php artisan package:discover

RUN mkdir -p \
    storage/app/docker \
    storage/app/public \
    storage/framework/cache/data \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs \
    bootstrap/cache \
    && chmod -R 775 storage bootstrap/cache

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=9000"]
