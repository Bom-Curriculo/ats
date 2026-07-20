<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;
use OpenApi\Attributes as OAT;

class UserResumeController extends Controller
{
    #[OAT\Get(
        path: '/client/user/resumes',
        summary: 'Lista os currículos gerados do usuário autenticado, do mais recente para o mais antigo',
        security: [['bearerAuth' => []]],
        tags: ['User'],
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Lista de currículos retornada com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Success'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(
                                    property: 'data',
                                    type: 'array',
                                    items: new OAT\Items(type: 'object')
                                ),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao listar os currículos',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Server error'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function __invoke(Request $request)
    {
        try {

            $resumes = UserResume::where('user_id', $request->user()->id)
                ->orderByDesc('created_at')
                ->get();

            return ResponseData::success('Success', [
                'data' => $resumes,
            ]);

        } catch (Exception $exception) {
            return ResponseData::error('Server error', [
                'error' => $exception->getMessage(),
            ],
                500);
        }
    }
}
