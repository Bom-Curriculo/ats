# syntax=docker/dockerfile:1

# =============================================================================
# Base, sistema, extensões PHP e Composer (compartilhado por dev e prod)
# =============================================================================
FROM php:8.4-fpm AS base

LABEL maintainer="bomcurriculo"

ENV TZ=America/Sao_Paulo \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    zip \
    sqlite3 \
    libzip-dev \
    libicu-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libonig-dev \
    libxml2-dev \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Timezone
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone

# Extensões do PHP
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" \
        bcmath \
        exif \
        gd \
        intl \
        opcache \
        pcntl \
        pdo_mysql \
        sockets \
        zip

# Extensão redis (REDIS_CLIENT=phpredis / horizon)
RUN pecl install redis \
    && docker-php-ext-enable redis

# Composer
COPY --from=composer:2.8 /usr/bin/composer /usr/local/bin/composer

WORKDIR /var/www/html

# =============================================================================
# Vendor, instala só as dependências de produção (cacheado)
# =============================================================================
FROM base AS vendor

COPY composer.json composer.lock ./

# --no-scripts: o artisan ainda não foi copiado; o package:discover roda depois.
# Cache de download do composer (BuildKit): re-tentativas reaproveitam.
RUN --mount=type=cache,target=/root/.composer/cache \
    composer install \
    --no-dev \
    --no-scripts \
    --prefer-dist \
    --no-progress \
    --optimize-autoloader

# =============================================================================
# Development, código vem via bind-mount; deps instaladas pelo entrypoint
# =============================================================================
FROM base AS development

ENV APP_ENV=local

COPY docker/php/php.dev.ini /usr/local/etc/php/conf.d/zz-app.ini
COPY docker/php/entrypoint.dev.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint

ENTRYPOINT ["entrypoint"]
CMD ["php-fpm"]

# =============================================================================
# Production, aplicação e dependências embutidas na imagem
# =============================================================================
FROM base AS production

ENV APP_ENV=production

COPY docker/php/php.prod.ini /usr/local/etc/php/conf.d/zz-app.ini

# Vendor de produção pré-instalado
COPY --from=vendor /var/www/html/vendor ./vendor

# Restante da aplicação
COPY . .

# Regenera o autoloader e roda o package:discover agora que o código existe
RUN composer dump-autoload --no-dev --optimize --classmap-authoritative

# Permissões e diretórios de runtime
RUN mkdir -p \
        storage/framework/cache \
        storage/framework/sessions \
        storage/framework/views \
        storage/logs \
        bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache \
    && chmod -R 775 storage bootstrap/cache

COPY docker/php/entrypoint.prod.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint

EXPOSE 9000

ENTRYPOINT ["entrypoint"]
CMD ["php-fpm"]
