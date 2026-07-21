<?php

namespace App\Http\Controllers;

use OpenApi\Attributes as OA;

#[OA\Info(
    title: 'Bom Currículo API',
    version: '1.0.0',
    description: 'API do Bom Currículo: autenticação, dados do usuário e geração de currículo.'
)]
#[OA\Server(
    url: L5_SWAGGER_CONST_HOST,
    description: 'Servidor da API'
)]
#[OA\SecurityScheme(
    securityScheme: 'sanctum',
    type: 'http',
    scheme: 'bearer',
    description: "Token obtido em /auth/login ou /auth/register. Envie como 'Bearer {token}'."
)]
abstract class Controller
{
    //
}
