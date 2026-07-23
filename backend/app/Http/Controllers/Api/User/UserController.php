<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\ApiRequests\Client\User\UpdateUserRequest;
use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use Exception;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;
use OpenApi\Attributes as OA;

#[OA\Tag(name: 'User', description: 'Perfil e dados do usuário autenticado')]
class UserController extends Controller
{
    use UserProcessRelationsTrait, UserUploadsTrait;

    #[OA\Put(
        path: '/client/user/update',
        tags: ['User'],
        summary: 'Atualiza o perfil do usuário (dados pessoais, arquivos e listas de skills/experiências/qualificações/idiomas/projetos)',
        description: 'multipart/form-data por causa dos uploads (resume_cv, resume_linkedin, path_certificate_pcd). Listas enviadas (skills, experiences, etc.) substituem as anteriores.',
        security: [['sanctum' => []]],
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\MediaType(
                mediaType: 'multipart/form-data',
                schema: new OA\Schema(
                    properties: [
                        new OA\Property(property: 'name', type: 'string'),
                        new OA\Property(property: 'password', type: 'string', format: 'password'),
                        new OA\Property(property: 'resume_cv', type: 'string', format: 'binary', description: 'PDF/DOC/DOCX, até 10MB'),
                        new OA\Property(property: 'resume_linkedin', type: 'string', format: 'binary', description: 'PDF/DOC/DOCX, até 10MB'),
                        new OA\Property(property: 'path_certificate_pcd', type: 'string', format: 'binary'),
                        new OA\Property(property: 'github_link', type: 'string', nullable: true),
                        new OA\Property(property: 'site_link', type: 'string', nullable: true),
                        new OA\Property(property: 'linkedin_link', type: 'string', nullable: true),
                        new OA\Property(property: 'social_name', type: 'string', nullable: true),
                        new OA\Property(property: 'phone', type: 'string', nullable: true),
                        new OA\Property(property: 'resume_email', type: 'string', format: 'email', nullable: true),
                        new OA\Property(property: 'gender', type: 'string', nullable: true),
                        new OA\Property(property: 'is_pcd', type: 'boolean', nullable: true),
                        new OA\Property(property: 'city', type: 'string', nullable: true),
                        new OA\Property(property: 'state', type: 'string', nullable: true),
                        new OA\Property(property: 'country', type: 'string', nullable: true),
                        new OA\Property(
                            property: 'skills', type: 'array',
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'name', type: 'string'),
                                new OA\Property(property: 'years', type: 'string', nullable: true),
                            ])
                        ),
                        new OA\Property(
                            property: 'experiences', type: 'array',
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'company', type: 'string'),
                                new OA\Property(property: 'role', type: 'string'),
                                new OA\Property(property: 'start', type: 'string', format: 'date'),
                                new OA\Property(property: 'end', type: 'string', format: 'date', nullable: true),
                                new OA\Property(property: 'description', type: 'string', nullable: true),
                                new OA\Property(property: 'is_actual', type: 'boolean'),
                                new OA\Property(property: 'city', type: 'string', nullable: true),
                                new OA\Property(property: 'state', type: 'string', nullable: true),
                                new OA\Property(property: 'country', type: 'string', nullable: true),
                            ])
                        ),
                        new OA\Property(
                            property: 'qualifications', type: 'array',
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'type', type: 'string', description: 'elementary_education | high_school | extracurricular_course | technical_course | undergraduate_degree | postgraduate_degree | master_degree | doctorate_degree'),
                                new OA\Property(property: 'institution', type: 'string'),
                                new OA\Property(property: 'title', type: 'string'),
                                new OA\Property(property: 'start', type: 'string', format: 'date'),
                                new OA\Property(property: 'end', type: 'string', format: 'date', nullable: true),
                                new OA\Property(property: 'is_coursing', type: 'boolean'),
                            ])
                        ),
                        new OA\Property(
                            property: 'languages', type: 'array',
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'level', type: 'string', description: 'beginner | intermediate | advanced | fluent | native'),
                                new OA\Property(property: 'language', type: 'string'),
                            ])
                        ),
                        new OA\Property(
                            property: 'projects', type: 'array',
                            items: new OA\Items(properties: [
                                new OA\Property(property: 'title', type: 'string'),
                                new OA\Property(property: 'date', type: 'string', description: 'ano, 4 dígitos'),
                                new OA\Property(property: 'technologies', type: 'string'),
                                new OA\Property(property: 'description', type: 'string'),
                                new OA\Property(property: 'url', type: 'string'),
                            ])
                        ),
                    ]
                )
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'Perfil atualizado',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'user', type: 'object'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 422, description: 'Erro de validação', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
            new OA\Response(response: 401, description: 'Não autenticado'),
        ]
    )]
    public function update(UpdateUserRequest $request)
    {

        try {

            DB::transaction(function () use ($request) {

                $user = $request->user();

                $this->processSkillsUser($request->input('skills', []), $user);
                $this->processExperiencesUser($request->input('experiences', []), $user);
                $this->processQualificationsUser($request->input('qualifications', []), $user);
                $this->processLanguageUser($request->input('languages', []), $user);
                $this->processProjectsUser($request->input('projects', []), $user);

                $pathResumeCv = $user->resume_cv;
                $pathResumeLinkedin = $user->resume_linkedin;
                $pathCertificatePCD = $user->path_certificate_pcd;

                if (! empty($request->file('resume_cv'))) {
                    $pathResumeCv = $this->storeCvResume($request, $user);
                }

                if (! empty($request->file('resume_linkedin'))) {
                    $pathResumeLinkedin = $this->storeLinkedinResume($request, $user);
                }

                if (! empty($request->file('path_certificate_pcd'))) {
                    $pathCertificatePCD = $this->storePcdCertificate($request, $user);
                }

                // Remove Files from request
                $request = $request->except([
                    'resume_cv',
                    'resume_linkedin',
                    'path_certificate_pcd',
                    'skills',
                    'experiences',
                    'qualifications',
                    'languages',
                ]);

                // Override Files path to request
                $data = array_merge([
                    'resume_cv' => $pathResumeCv,
                    'resume_linkedin' => $pathResumeLinkedin,
                    'path_certificate_pcd' => $pathCertificatePCD,
                ], $request);

                $user->update($data);
            });

            return ResponseData::success('Success', [
                'user' => $request->user()->load(['skills', 'experiences', 'qualifications', 'languages', 'projects']),
            ]);

        } catch (ValidationException $validator) {

            return ResponseData::error('Validation failed.', [
                'errors' => $validator->errors(),
            ],
                422);

        } catch (Exception $exception) {

            return ResponseData::error('Server error', [
                'error' => $exception->getMessage(),
            ],
                500);

        }
    }
}
