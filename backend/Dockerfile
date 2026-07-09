FROM php:8.4-cli

LABEL maintainer="servidor de tecnologia"

ENV TZ=America/Sao_Paulo

RUN apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*


RUN docker-php-ext-configure gd \
    --with-freetype \
    --with-jpeg


RUN docker-php-ext-install \
    bcmath \
    exif \
    gd \
    intl \
    opcache \
    pcntl \
    pdo_pgsql \
    pgsql \
    sockets \
    zip

RUN pecl install redis \
    && docker-php-ext-enable redis


COPY --from=composer:2.8 /usr/bin/composer /usr/local/bin/composer


WORKDIR /var/www/html

COPY composer.json composer.lock ./

RUN composer install \
    --prefer-dist \
    --no-interaction \
    --no-progress \
    --no-scripts

COPY . .

RUN composer dump-autoload --optimize

RUN php artisan package:discover

RUN mkdir -p \
    storage/framework/cache \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs \
    bootstrap/cache
    
RUN chmod -R 775 storage bootstrap/cache

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["entrypoint.sh"]

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=9000"]