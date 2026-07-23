<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;
use OpenApi\Attributes as OA;

class UserResumeController extends Controller
{
    #[OA\Get(
        path: '/client/user/resumes',
        tags: ['User'],
        summary: 'Lista os currículos gerados pelo usuário, do mais recente pro mais antigo',
        security: [['sanctum' => []]],
        responses: [
            new OA\Response(
                response: 200,
                description: 'Lista de currículos',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'data', type: 'array', items: new OA\Items(type: 'object')),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 401, description: 'Não autenticado'),
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
