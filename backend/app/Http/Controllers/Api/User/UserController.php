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
use OpenApi\Attributes as OAT;

class UserController extends Controller
{
    use UserProcessRelationsTrait, UserUploadsTrait;

    #[OAT\Put(
        path: '/client/user/update',
        summary: 'Atualiza os dados do usuário autenticado, incluindo currículo, habilidades, experiências, qualificações, idiomas e projetos',
        security: [['bearerAuth' => []]],
        tags: ['User'],
        requestBody: new OAT\RequestBody(
            required: false,
            content: new OAT\MediaType(
                mediaType: 'multipart/form-data',
                schema: new OAT\Schema(
                    properties: [
                        new OAT\Property(property: 'name', type: 'string', example: 'João da Silva'),
                        new OAT\Property(property: 'password', type: 'string', format: 'password'),
                        new OAT\Property(property: 'resume_cv', type: 'string', format: 'binary', description: 'Arquivo do currículo (pdf, doc ou docx)'),
                        new OAT\Property(property: 'resume_linkedin', type: 'string', format: 'binary', description: 'Export do PDF do LinkedIn'),
                        new OAT\Property(property: 'path_certificate_pcd', type: 'string', format: 'binary', nullable: true),
                        new OAT\Property(property: 'github_link', type: 'string', nullable: true),
                        new OAT\Property(property: 'site_link', type: 'string', nullable: true),
                        new OAT\Property(property: 'linkedin_link', type: 'string', nullable: true),
                        new OAT\Property(property: 'social_name', type: 'string', nullable: true),
                        new OAT\Property(property: 'phone', type: 'string', nullable: true),
                        new OAT\Property(property: 'resume_email', type: 'string', format: 'email', nullable: true),
                        new OAT\Property(property: 'gender', type: 'string', nullable: true, description: 'Ver enum UserGenderEnum'),
                        new OAT\Property(property: 'is_pcd', type: 'boolean', nullable: true),
                        new OAT\Property(property: 'city', type: 'string', nullable: true),
                        new OAT\Property(property: 'state', type: 'string', nullable: true),
                        new OAT\Property(property: 'country', type: 'string', nullable: true),
                        new OAT\Property(
                            property: 'skills',
                            type: 'array',
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'name', type: 'string'),
                                    new OAT\Property(property: 'years', type: 'string', nullable: true),
                                ]
                            )
                        ),
                        new OAT\Property(
                            property: 'experiences',
                            type: 'array',
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'company', type: 'string'),
                                    new OAT\Property(property: 'role', type: 'string'),
                                    new OAT\Property(property: 'start', type: 'string', format: 'date'),
                                    new OAT\Property(property: 'end', type: 'string', format: 'date', nullable: true),
                                    new OAT\Property(property: 'description', type: 'string', nullable: true),
                                    new OAT\Property(property: 'is_actual', type: 'boolean'),
                                    new OAT\Property(property: 'city', type: 'string', nullable: true),
                                    new OAT\Property(property: 'state', type: 'string', nullable: true),
                                    new OAT\Property(property: 'country', type: 'string', nullable: true),
                                ]
                            )
                        ),
                        new OAT\Property(
                            property: 'qualifications',
                            type: 'array',
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'type', type: 'string', description: 'Ver enum UserQualificationTypeEnum'),
                                    new OAT\Property(property: 'institution', type: 'string'),
                                    new OAT\Property(property: 'title', type: 'string'),
                                    new OAT\Property(property: 'start', type: 'string', format: 'date'),
                                    new OAT\Property(property: 'end', type: 'string', format: 'date', nullable: true),
                                    new OAT\Property(property: 'is_coursing', type: 'boolean'),
                                ]
                            )
                        ),
                        new OAT\Property(
                            property: 'languages',
                            type: 'array',
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'level', type: 'string', description: 'Ver enum UserLanguageLevelEnum'),
                                    new OAT\Property(property: 'language', type: 'string'),
                                ]
                            )
                        ),
                        new OAT\Property(
                            property: 'projects',
                            type: 'array',
                            items: new OAT\Items(
                                properties: [
                                    new OAT\Property(property: 'title', type: 'string'),
                                    new OAT\Property(property: 'date', type: 'string', description: 'Ano com 4 dígitos'),
                                    new OAT\Property(property: 'technologies', type: 'string'),
                                    new OAT\Property(property: 'description', type: 'string'),
                                    new OAT\Property(property: 'url', type: 'string'),
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
                description: 'Usuário atualizado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Success'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'user', type: 'object'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
            new OAT\Response(response: 422, description: 'Erro de validação', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao atualizar o usuário',
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
