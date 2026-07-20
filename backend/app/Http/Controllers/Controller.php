<?php

namespace App\Http\Controllers;

use OpenApi\Attributes as OAT;

#[OAT\Info(
    title: 'Bom Currículo API',
    version: '1.0.0',
    description: 'API para geração e gestão de currículos com IA'
)]
#[OAT\Server(url: '/api', description: 'Servidor da API')]
#[OAT\SecurityScheme(
    securityScheme: 'bearerAuth',
    type: 'http',
    scheme: 'bearer',
    bearerFormat: 'Sanctum Token'
)]
#[OAT\Schema(
    schema: 'ValidationErrorResponse',
    description: 'Erro de validação de um FormRequest. Todo FormRequest da API estende CustomRequest, cujo failedValidation() sempre responde com esta mesma mensagem, independentemente do endpoint.',
    properties: [
        new OAT\Property(property: 'code', type: 'integer', example: 422),
        new OAT\Property(property: 'message', type: 'string', example: 'Data validation errors'),
        new OAT\Property(
            property: 'data',
            type: 'object',
            properties: [
                new OAT\Property(
                    property: 'errors',
                    type: 'object',
                    additionalProperties: new OAT\AdditionalProperties(
                        type: 'array',
                        items: new OAT\Items(type: 'string')
                    ),
                    example: ['email' => ['The email field is required.']]
                ),
            ]
        ),
    ]
)]
#[OAT\Schema(
    schema: 'UnauthenticatedResponse',
    description: 'Resposta padrão do middleware auth:sanctum quando nenhum token válido é enviado. Não segue o envelope {code,message,data} do restante da API, pois é gerada pelo próprio framework antes de chegar ao controller.',
    properties: [
        new OAT\Property(property: 'message', type: 'string', example: 'Unauthenticated.'),
    ]
)]
abstract class Controller
{
    //
}
