<?php

namespace App\Services\RabbitMQ\Resume\Response;

use App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingConsumer;
use App\Services\RabbitMQ\Resume\DTO\ResumeResponseDTO;
use Exception;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class ProcessResumeResponse
{
    public static function handle(array $data = [], bool $useFake = false)
    {

        try {

            if ($useFake) {
                $data = self::fakeData();
            }

            $resumeProcesses = (array) ResumeResponseDTO::fromData($data)->handle()->toArray();
            ResumeProcessingConsumer::dispatch($resumeProcesses)
                ->onConnection('redis');

        } catch (Exception $exception) {
            Log::channel('rabbit_resumes')->error(
                'Consumer Resume Process failed',
                [
                    'error' => $exception->getMessage(),
                    'class' => __CLASS__,
                    'exception' => $exception,
                ]
            );
        }

    }

    protected static function fakeData(): array
    {
        // Just for remember, remove later
        return [

            // Is required ?
            'analysis_request_id' => Str::uuid(),

            // REQUIRED: user_id
            'user_id' => 1,

            // Status of process
            'status' => 'teste',

            // Result of processing Resume
            'result' => [

                // Score of resume
                'score' => rand(0, 100),

                // Suggestion
                'suggestion' => 'Maybe anything',

                // Header to generate resume
                'header' => [
                    'name' => 'Jhon Due',
                    'headline' => 'Desenvolvedor Backend Júnior | Java • Python • Spring Boot • FastAPI • IA Aplicada',
                    'email' => 'email@test.com',
                    'location' => 'Rua tal, Sao paulo/SP',
                    'contacts' => '(11) 91903-0102 / (11) 91903-0102',
                    'emails' => 'test@example.com / company@exampe.com',
                    'links' => [
                        // Return as the key the original name.
                        'Portfolio' => '',
                    ],
                ],

                // Experiences
                'experiences' => [
                    [
                        'company' => 'Bom Curriculo',
                        'role' => 'Desenvolvedor Backend',
                        'start' => '2026-07-01',
                        'end' => null, // Null | Date
                        'description' => 'Realizado o backend', // Null | String
                        'is_actual' => true, // Null | String
                        'city' => 'São Paulo', // Null | String
                        'state' => 'SP', // Null | String
                        'country' => null, // Null | String
                    ],
                ],

                // Projects
                'projects' => [
                    [
                        'title' => 'Bom Curriculo',
                        'date' => '2026',
                        'technologies' => null, // null | string
                        'description' => null, // null | string
                        'url' => null, // null | string
                    ],
                ],

                // Qualifications
                'qualifications' => [
                    [
                        /**
                         * type property
                         *
                         * pt_BR: Tipo de instituição
                         *
                         * Enum:
                         *  elementary_education,
                         *  high_school,
                         *  extracurricular_course,
                         *  technical_course
                         *  undergraduate_degree
                         *  postgraduate_degree
                         *  master_degree
                         *  doctorate_degree
                         */
                        'type' => 'elementary_education',
                        'institution' => 'Instituicao',
                        'title' => 'Curso',
                        'start' => '2026-01-01',
                        'end' => null,  // Null | Date
                        'is_coursing' => true, // Boolean,
                    ],
                ],

                // Skills
                'skills' => [
                    [
                        'name' => 'PHP',
                        'years' => null, // Null | int
                    ],
                ],

                // Languages
                'languages' => [
                    [
                        /**
                         * level property
                         *
                         * pt_BR: Nível
                         *
                         * Enum:
                         *  beginner,
                         *  intermediate,
                         *  advanced,
                         *  fluent
                         *  native
                         */
                        'level' => 'native',
                        'language' => 'portugues',
                    ],
                ],

                // Another informations
                'others' => [
                    // all another informations here,
                    // this will be stored, but never used
                    // just to persist on database
                    'something' => 'teste',
                    'data' => [
                        'test',
                    ],
                ],

            ],

            // Bot Errors
            'error' => '',
        ];
    }
}
