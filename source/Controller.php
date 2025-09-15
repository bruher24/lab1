<?php

class Controller
{
    protected PDO $db;

    public function __construct()
    {
        ///home/bruher/projects/lab1/source/db/database.db
        $path = dirname(__DIR__) . '/source/db/database.db';
        $this->db = new PDO("sqlite:$path");
    }

    public function home(): void
    {
        $path = dirname(__DIR__) . '/public/index.html';
        $html = file_get_contents($path);
        echo $html;
    }

    public function index(): void
    {
        $variants = $this->db->query('SELECT * FROM variants')->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode([
            'success' => true,
            'variants' => $variants,
        ]);
    }

    public function store(): string
    {
        var_dump($_POST);
    }

    public function show(string $variant_id): string
    {
        if (!is_numeric($variant_id)) {
            return self::errorResponse('Variant ID must be numeric');
        }
        echo 'show';
    }

    public function scheme(): string
    {
        echo 'scheme';
    }

    private function successResponse(string $message, array $data = []): string
    {
    }

    private function errorResponse(string $message): string
    {
        return json_encode($message, JSON_PRETTY_PRINT);
    }
}
