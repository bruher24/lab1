<?php

class Controller
{
    private PDO $db;
    public function __construct()
    {
        $this->db = new PDO("sqlite:database.db");
    }

    public static function home(): void
    {
        $path = dirname(__DIR__) . '/public/index.html';
        $html = file_get_contents($path);
        echo $html;
    }

    public static function index(): string
    {
        echo 'index';
    }

    public static function store(): string
    {
        var_dump($_POST);
    }

    public static function show(string $variant_id): string
    {
        if (!is_numeric($variant_id)) {
            return self::errorResponse('Variant ID must be numeric');
        }
        echo 'show';
    }

    public static function scheme(): string
    {
        echo 'scheme';
    }

    private static function successResponse(string $message, array $data = []): string
    {

    }

    private static function errorResponse(string $message): string
    {
        return json_encode($message, JSON_PRETTY_PRINT);
    }
}
