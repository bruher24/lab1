<?php

try {
    $db = new PDO("sqlite:database.db");
    $query = "CREATE TABLE IF NOT EXISTS variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT NOT NULL UNIQUE,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )";
    $stmt = $db->prepare($query);
    $stmt->execute();

    $query = "INSERT INTO variants (name, question, answer)
        VALUES (:name, :question, :answer)
        ON CONFLICT(name) DO UPDATE SET
            question = excluded.question, 
            answer = excluded.answer";
    $stmt = $db->prepare($query);

    $data = [
        'name' => 'cat',
        'question' => 'meow?',
        'answer' => 'yes'
    ];

    $stmt->execute($data);
    $db = null;
} catch (PDOException $e) {
    die($e->getMessage());
}
