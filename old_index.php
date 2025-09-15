<?php

require_once 'db.php';

$db = new PDO("sqlite:database.db");

$res = $db->query("SELECT * FROM variants");
$res->setFetchMode(PDO::FETCH_ASSOC);

$variants = $res->fetchAll();
$pointer = 0;
$result = guess($variants);
if (empty($result)) {
    $newVariant = addNewVariant();
    if (storeNewVariant($newVariant)) {
        exit("Thanks, stored \033[33m" . $newVariant['name'] . "\033[0m to database" . PHP_EOL);
    }
}
echo $result . PHP_EOL;
$button = showMenu();

function showMenu() {
    return readline("1.Play\n2.Add\n3.Show DB" . PHP_EOL);
}

function guess(array $variants): string
{
    global $pointer;
    foreach ($variants as $variant) {
        if ($pointer == 0) {
            $pointer = 1;
            $answer = readline($variant['name'] . '?' . PHP_EOL);
            if ($answer == 'yes') {
                return 'GG: ' . $variant['name'] . PHP_EOL;
            }
            continue;
        }
        $answer = readline($variant['question'] . PHP_EOL);
        if ($answer == 'yes') {
            $answer = readline($variant['name'] . '?' . PHP_EOL);
            if ($answer == 'yes') {
                return 'GG: ' . $variant['name'] . PHP_EOL;
            }
        }
    }
    return '';
}

function addNewVariant(): array
{
    $newVariant['name'] = getNewName();
    $newVariant['question'] = getNewQuestion();
    $newVariant['answer'] = getNewAnswer();
    return $newVariant;
}

function getNewName(): string
{
    $name = trim(readline("What is it\033[33m name \033[0m?" . PHP_EOL));
    if (strlen($name) > 50 || strlen($name) < 3) {
        echo "\033[33mName \033[0m must contain 3 to 50 characters." . PHP_EOL;
        return getNewName();
    }
    return ucfirst($name);
}

function getNewQuestion(): string
{
    $question = trim(readline("What is it \033[33m question \033[0m?" . PHP_EOL));
    if (strlen($question) > 50 || strlen($question) < 3) {
        echo "\033[33mQuestion \033[0m must contain 3 to 50 characters." . PHP_EOL;
        return getNewQuestion();
    }
    if (!str_ends_with($question, '?')) {
        $question .= '?';
    }
    return ucfirst($question);
}

function getNewAnswer(): string
{
    $answer = trim(readline("What is it \033[33m answer \033[0m?" . PHP_EOL));
    if (!in_array($answer, ['Yes', 'No'])) {
        echo "\033[33mAnswer \033[0m must be only \033[32m yes \033[0m or \033[31m no \033[0m." . PHP_EOL;
        return getNewAnswer();
    }
    return ucfirst($answer);
}

function storeNewVariant(array $variant): bool
{
    global $db;
    $stmt = $db->prepare("INSERT INTO variants (name, question, answer) VALUES (:name, :question, :answer)");
    if (!$stmt->execute($variant)) {
        return false;
    }
    return true;
}
