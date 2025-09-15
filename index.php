<?php
require_once 'source/Router.php';
require_once 'source/Controller.php';

$router = new Router();
$router->add('GET', '/', [Controller::class, 'home']);
$router->add('GET', '/variants', [Controller::class, 'index']);
$router->add('POST', '/variants/store', [Controller::class, 'store']);
$router->add('GET', '/variants/{variant_id}', [Controller::class, 'show']);
$router->add('GET', '/scheme', [Controller::class, 'scheme']);

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestMethod = $_SERVER['REQUEST_METHOD'];

$router->dispatch($requestUri, $requestMethod);
