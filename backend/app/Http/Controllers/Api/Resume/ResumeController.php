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
use OpenApi\Attributes as OA;

#[OA\Tag(name: 'Resume', description: 'Upload, listagem e status dos currículos')]
class ResumeController extends Controller
{
    use UserProcessRelationsTrait, UserUploadsTrait;

    #[OA\Post(
        path: '/client/resumes/new-resume',
        tags: ['Resume'],
        summary: 'Envia um novo currículo (CV e/ou LinkedIn) pra análise da IA',
        security: [['sanctum' => []]],
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\MediaType(
                mediaType: 'multipart/form-data',
                schema: new OA\Schema(
                    properties: [
                        new OA\Property(property: 'resume_cv', type: 'string', format: 'binary', description: 'PDF/DOC/DOCX, até 10MB'),
                        new OA\Property(property: 'resume_linkedin', type: 'string', format: 'binary', description: 'PDF/DOC/DOCX, até 10MB'),
                        new OA\Property(property: 'github_link', type: 'string', nullable: true),
                        new OA\Property(property: 'site_link', type: 'string', nullable: true),
                        new OA\Property(
                            property: 'skills', type: 'array', nullable: true,
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'name', type: 'string'),
                            ])
                        ),
                    ]
                )
            )
        ),
        responses: [
            new OA\Response(response: 200, description: 'Upload processado', content: new OA\JsonContent(ref: '#/components/schemas/ApiSuccessResponse')),
            new OA\Response(response: 422, description: 'Erro de validação', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
            new OA\Response(response: 401, description: 'Não autenticado'),
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

    #[OA\Get(
        path: '/client/resumes/files',
        tags: ['Resume'],
        summary: 'Gera um link temporário (24h) pra baixar um arquivo do usuário',
        security: [['sanctum' => []]],
        parameters: [
            new OA\Parameter(
                name: 'type', in: 'query', required: false,
                description: 'Qual arquivo buscar. Padrão: cv',
                schema: new OA\Schema(type: 'string', enum: ['cv', 'linkedin', 'pcd'], default: 'cv')
            ),
        ],
        responses: [
            new OA\Response(
                response: 200,
                description: 'URL temporária gerada',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'file_url', type: 'string'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 404, description: 'Arquivo não encontrado', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Get(
        path: '/client/resumes/pendings',
        tags: ['Resume'],
        summary: 'Lista as análises de currículo do usuário (histórico/status de processamento)',
        security: [['sanctum' => []]],
        responses: [
            new OA\Response(
                response: 200,
                description: 'Lista de análises',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'array', items: new OA\Items(type: 'object')),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 401, description: 'Não autenticado'),
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

    #[OA\Get(
        path: '/client/resumes/pendings/{resume}',
        tags: ['Resume'],
        summary: 'Detalha uma análise de currículo específica do usuário',
        security: [['sanctum' => []]],
        parameters: [
            new OA\Parameter(
                name: 'resume', in: 'path', required: true,
                description: 'ID do registro de análise (ResumeAnalytic)',
                schema: new OA\Schema(type: 'integer')
            ),
        ],
        responses: [
            new OA\Response(response: 200, description: 'Análise encontrada', content: new OA\JsonContent(ref: '#/components/schemas/ApiSuccessResponse')),
            new OA\Response(response: 404, description: 'Não encontrada ou não pertence ao usuário', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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
