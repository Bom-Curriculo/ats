<?php

namespace App\Services\RabbitMQ\Resume;

use App\Helpers\ResponseData;
use App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;
use OpenApi\Attributes as OA;

#[OA\Tag(name: 'Resume', description: 'Upload, listagem e status dos currículos')]
class ProducerResumesService
{
    #[OA\Post(
        path: '/client/services/rabbitmq/process',
        tags: ['Resume'],
        summary: 'Dispara o processamento de um currículo do usuário na fila (RabbitMQ)',
        security: [['sanctum' => []]],
        requestBody: new OA\RequestBody(
            content: new OA\JsonContent(
                properties: [
                    new OA\Property(property: 'user_resume_id', type: 'integer', nullable: true, description: 'ID do currículo a processar; se omitido, usa o mais recente'),
                ]
            )
        ),
        responses: [
            new OA\Response(response: 200, description: 'Enviado pra fila com sucesso', content: new OA\JsonContent(ref: '#/components/schemas/ApiSuccessResponse')),
            new OA\Response(response: 404, description: 'Currículo não encontrado pra esse usuário', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
        ]
    )]
    public function __invoke(Request $request)
    {
        try {

            if (! $request->filled('user_resume_id')) {
                $resume = UserResume::find($request->input('user_resume_id'));
                if ($resume && $request->user()->id !== $resume->user_id) {
                    return ResponseData::success('Not found!', [
                        'message' => 'Resume not found for this user.',
                    ], 404);
                }
            }

            ResumeProcessingPublisher::dispatch($request->user(), $request->user_resume_id ?? null)->onConnection('rabbitmq_producer');

            return ResponseData::success('Success', [
                'message' => 'Processed to worker successfuly',
            ], 200);

        } catch (Exception $exception) {
            return ResponseData::error('Failed',
                [
                    'message' => $exception->getMessage(),
                ], 500);
        }

    }
}
