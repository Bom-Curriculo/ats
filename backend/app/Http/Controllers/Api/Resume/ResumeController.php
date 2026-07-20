<?php

namespace App\Http\Controllers\Api\Resume;

use App\Helpers\ResponseData;
use App\Http\ApiRequests\Client\Resume\NewResumeRequest;
use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use App\Models\ResumeAnalytic;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\ValidationException;
use OpenApi\Attributes as OAT;

class ResumeController extends Controller
{
    use UserProcessRelationsTrait, UserUploadsTrait;

    #[OAT\Post(
        path: '/client/resumes/new-resume',
        summary: 'Envia um novo currículo (CV e/ou export do LinkedIn) e atualiza os dados do usuário',
        security: [['bearerAuth' => []]],
        tags: ['Resume'],
        requestBody: new OAT\RequestBody(
            required: false,
            content: new OAT\MediaType(
                mediaType: 'multipart/form-data',
                schema: new OAT\Schema(
                    properties: [
                        new OAT\Property(property: 'resume_cv', type: 'string', format: 'binary', description: 'Arquivo do currículo (pdf, doc ou docx)'),
                        new OAT\Property(property: 'resume_linkedin', type: 'string', format: 'binary', description: 'Export do PDF do LinkedIn'),
                        new OAT\Property(property: 'github_link', type: 'string', nullable: true),
                        new OAT\Property(property: 'site_link', type: 'string', nullable: true),
                        new OAT\Property(
                            property: 'skills',
                            type: 'array',
                            nullable: true,
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'name', type: 'string'),
                                ]
                            )
                        ),
                    ]
                )
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Currículo processado e usuário atualizado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'User Updated'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'message', type: 'string', example: 'User and upload has been updated.'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
            new OAT\Response(response: 422, description: 'Erro de validação', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao processar o currículo',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Server Error'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'errors', type: 'string', description: 'Mensagem da exceção (nota: aqui é uma string, diferente do padrão {error: string} usado no restante da API)'),
                            ]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function storeNewResume(NewResumeRequest $request)
    {

        try {

            DB::transaction(function () use ($request) {
                $user = $request->user();

                $resumeCV = $request->file('resume_cv');
                $resumeLinkedin = $request->file('resume_linkedin');

                $pathResumeCv = null;
                $pathResumeLinkedin = null;
                $skills = $request->input('skills', []);

                if (! empty($resumeCV)) {
                    $pathResumeCv = $this->storeCvResume($request, $user);
                }

                if (! empty($resumeLinkedin)) {
                    $pathResumeLinkedin = $this->storeLinkedinResume($request, $user);
                }

                $user->update([
                    'resume_cv' => $pathResumeCv ?? $user->resumeCV,
                    'resume_linkedin' => $pathResumeLinkedin ?? $user->resume_linkedin,
                    'github_link' => $request->input('github_link', $user->github_link),
                    'site_link' => $request->input('site_link', $user->site_link),
                ]);

                if (! empty($pathResumeCv) || ! empty($pathResumeLinkedin)) {
                    $user->resumes()->create([
                        'original_file_path_cv' => $pathResumeCv,
                        'original_file_path_linkedin' => $pathResumeLinkedin,
                    ]);
                }
                $this->processSkillsUser($skills, $user);

            });

            return ResponseData::success('User Updated', ['message' => 'User and upload has been updated.'], 200);

        } catch (ValidationException $exception) {
            return ResponseData::error('Validation error', ['errors' => $exception->errors()], 422);
        } catch (Exception $exception) {
            return ResponseData::error('Server Error', ['errors' => $exception->getMessage()], 500);
        }
    }

    #[OAT\Get(
        path: '/client/resumes/files',
        summary: 'Gera uma URL temporária para download de um arquivo do usuário (CV, LinkedIn ou certificado PCD)',
        security: [['bearerAuth' => []]],
        tags: ['Resume'],
        parameters: [
            new OAT\Parameter(
                name: 'type',
                in: 'query',
                required: false,
                description: 'Tipo de arquivo desejado. Padrão: cv',
                schema: new OAT\Schema(type: 'string', enum: ['cv', 'linkedin', 'pcd'], default: 'cv')
            ),
        ],
        responses: [
            new OAT\Response(
                response: 200,
                description: 'URL temporária gerada com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'success'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'file_url', type: 'string', format: 'uri'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
            new OAT\Response(
                response: 404,
                description: 'Arquivo não encontrado',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 404),
                        new OAT\Property(property: 'message', type: 'string', example: 'Not Found'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string', example: 'The requested file has not found.')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function getResumesFiles(Request $request)
    {
        $user = $request->user();
        $type = $request->input('type', 'cv');

        $typeFile = match ($type) {
            'cv' => $user->resume_cv,
            'linkedin' => $user->resume_linkedin,
            'pcd' => $user->path_certificate_pcd,
            default => $user->resume_cv,
        };

        if (! $typeFile || ! Storage::exists($typeFile)) {
            return ResponseData::error('Not Found', [
                'error' => 'The requested file has not found.',
            ], 404);
        }

        $fileUrl = Storage::temporaryUrl($typeFile, now()->addDay());

        return ResponseData::success('success', [
            'file_url' => $fileUrl,
        ], 200);

    }

    #[OAT\Get(
        path: '/client/resumes/pendings',
        summary: 'Lista as análises de currículo (pendentes ou concluídas) do usuário autenticado',
        security: [['bearerAuth' => []]],
        tags: ['Resume'],
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Lista de análises retornada com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Success'),
                        new OAT\Property(
                            property: 'data',
                            type: 'array',
                            items: new OAT\Items(type: 'object')
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
        ]
    )]
    public function resumeAnalytics(Request $request)
    {
        return ResponseData::success(
            'Success',
            $request->user()->resumeAnalytics()->orderByDesc('created_at')->get()->toArray(),
            200
        );
    }

    #[OAT\Get(
        path: '/client/resumes/pendings/{resume}',
        summary: 'Retorna os detalhes de uma análise de currículo específica do usuário autenticado',
        security: [['bearerAuth' => []]],
        tags: ['Resume'],
        parameters: [
            new OAT\Parameter(
                name: 'resume',
                in: 'path',
                required: true,
                description: 'ID da análise de currículo (ResumeAnalytic)',
                schema: new OAT\Schema(type: 'integer')
            ),
        ],
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Análise de currículo retornada com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Success'),
                        new OAT\Property(property: 'data', type: 'object'),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
            new OAT\Response(
                response: 404,
                description: 'Análise não encontrada ou pertence a outro usuário',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 404),
                        new OAT\Property(property: 'message', type: 'string', example: 'Not found'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string', example: 'Resume not found')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function showPendingResume(Request $request, int $resume)
    {

        $resume = (int) $request->resume;
        $resume = ResumeAnalytic::find($resume);

        if (! $resume || $resume->user_id !== $request->user()->id) {
            return ResponseData::error(
                'Not found',
                [
                    'error' => 'Resume not found',
                ],
                404
            );
        }

        return ResponseData::success(
            'Success',
            $resume->toArray(),
            200
        );
    }
}
