FROM php:8.2-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql \
    && a2enmod rewrite

# 응답 charset을 UTF-8로 강제 (한글 mojibake 방지)
COPY apache-utf8.conf /etc/apache2/conf-available/utf8.conf
RUN a2enconf utf8

# PHP 기본 charset도 UTF-8로
RUN { \
      echo 'default_charset = "UTF-8"'; \
      echo 'mbstring.internal_encoding = UTF-8'; \
    } > /usr/local/etc/php/conf.d/utf8.ini

EXPOSE 80
