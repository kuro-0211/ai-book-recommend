<?php
/**
 * MySQL PDO 연결 헬퍼.
 * docker-compose의 환경변수로부터 접속 정보를 받음.
 */
function get_pdo(): PDO {
    $host = getenv('MYSQL_HOST') ?: 'mysql';
    $port = getenv('MYSQL_PORT') ?: '3306';
    $db   = getenv('MYSQL_DATABASE') ?: 'bookrec';
    $user = getenv('MYSQL_USER') ?: 'bookuser';
    $pass = getenv('MYSQL_PASSWORD') ?: '';

    $dsn = "mysql:host={$host};port={$port};dbname={$db};charset=utf8mb4";
    $opts = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
    ];
    return new PDO($dsn, $user, $pass, $opts);
}
