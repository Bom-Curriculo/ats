<?php

namespace App\Jobs\Api\RabbitMQ\Resumes;

use App\Models\User;
use App\Models\UserResume;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Storage;

class ResumeProcessingPublisher implements ShouldQueue
{
    use Queueable;

    public $user_id = null;
    public $resume_id = null;
    public $resume_cv = null;
    public $resume_linkedin = null;
    public $expires_link;
    public $github_link;
    public $site_link;
    private $userResume = null;

    /**
     * Create a new job instance.
     */
    public function __construct(

        User $user,
        ?UserResume $userResume = null

    )
    {
        $this->user_id = $user->id;
        $this->expires_link = now()->addDay();

        if($userResume && $userResume->id !== null)
        {

            $this->resume_id = $userResume->id;

            if(!empty($userResume->original_file_path_cv)){
                $this->resume_cv = Storage::temporaryUrl($userResume->original_file_path_cv, $this->expires_link);
            }

            if(!empty($userResume->original_file_path_linkedin)){
                $this->resume_linkedin = Storage::temporaryUrl($userResume->original_file_path_linkedin, $this->expires_link);
            }

        }else{

            if(!empty($user->resume_cv)){
                $this->resume_cv = Storage::temporaryUrl($user->resume_cv, $this->expires_link);
            }

            if(!empty($user->resume_linkedin)){
                $this->resume_linkedin = Storage::temporaryUrl($user->resume_linkedin, $this->expires_link);
            }

        }

        if(!empty($user->github_link)){
            $this->github_link = $user->github_link;
        }

        if(!empty($user->site_link)){
            $this->site_link = $user->site_link;
        }

    }

    public function getConnectionName(): ?string
    {
        return 'rabbitmq_producer';
    }

    /**
     * Execute the job.
     */
    
}
