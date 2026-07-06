<?php

namespace App\Services\RabbitMQ\Resume\DTO;

use Illuminate\Support\Facades\Log;
use InvalidArgumentException;

final class ResumeResponseDTO 
{

    private const REQUIREMENTS = [
        'analysis_request_id',
        'user_id',
        'status',
        'result',
        'error'
    ];
  
    public function __construct(
        public string $analysis_request_id,
        public int $user_id,
        public string $status,
        public array $result,
        public null|string|array|object $error,

        public array $header = [],

        public array $experiences = [],
        public array $projects = [],
        public array $qualifications = [],
        public array $skills = [],
        public array $languages = [],
        public array $others = [],
 
    ) {}


    public static function fromData(array|object $data): self
    {

        $dataArray = is_object($data) ? (array) $data : $data;

        foreach (self::REQUIREMENTS as $requirement) {
            if (!array_key_exists($requirement, $dataArray)) {
                
                Log::channel('rabbit_resumes')->error('RabbitMQ Consumer fail', [
                    'error' => "Missing required field from BOT: {$requirement}",
                    'payload' => $dataArray
                ]);
                
                throw new InvalidArgumentException("Missing required field: {$requirement}");
            }
        }

        return new self(
            analysis_request_id: (string) $dataArray['analysis_request_id'],
            user_id: (int) $dataArray['user_id'],
            status: (string) $dataArray['status'],
            result: (array) $dataArray['result'],
            error: $dataArray['error'] ?? null,
            qualifications: $dataArray['qualifications'] ?? [],
            projects: $dataArray['projects'] ?? []
        );
    }

    public function handle()
    {
        $this->processHeader();
        $this->processSkills();
        $this->processExperiences();
        $this->processProjects();
        $this->processQualifications();
        $this->processLanguages();
        $this->proccessOthers();

        return $this;
    }

    public function debug()
    {
        dd($this); 
    }

    public function toArray(): array
    {
        return [
            'analysis_request_id' => $this->analysis_request_id,
            'user_id'             => $this->user_id,
            'status'              => $this->status,
            'error'               => $this->error,
            'header'              => $this->header,
            'experiences'         => $this->experiences,
            'projects'            => $this->projects,
            'qualifications'      => $this->qualifications,
            'skills'              => $this->skills,
            'languages'           => $this->languages,
            'others'              => $this->others,
        ];
    }

    protected function processheader(){
        
        // Implement: Header Validation

        $this->header = $this->result['header'] ?? [];
    }

    protected function processSkills(){

        // Implement: Skills Validation

        $this->skills = $this->result['skills'] ?? [];
    }

    protected function processExperiences(){

        // Implement: Experiences Validation

        $this->experiences = $this->result['experiences'] ?? [];
    }

    protected function processProjects(){

        // Implement: Projects Validation

        $this->projects = $this->result['projects'] ?? [];
    }

    protected function processQualifications(){

        // Implement: Qualifications Validation

        $this->qualifications = $this->result['qualifications'] ?? [];
    }

    protected function processLanguages(){

        // Implement: Languages Validation

        $this->languages = $this->result['languages'] ?? [];
    }

    protected function proccessOthers()
    {   

        // Don't implements validations here

        $this->others = $this->result['others'] ?? [];
    }

}