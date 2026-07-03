<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Storage;

class ProccessResumesJobs implements ShouldQueue
{
    use Queueable;

    protected $user_id = null;
    protected $resume_cv = null;
    protected $resume_linkedin = null;
    protected $expires_link;

    /**
     * Create a new job instance.
     */
    public function __construct(
        User $user
    )
    {
        $this->user_id = $user->id;
        $this->expires_link = now()->addDay();

        if(!empty($user->resume_cv)){
            $this->resume_cv = Storage::temporaryUrl($user->resume_cv, $this->expires_link);
        }

        if(!empty($user->resume_linkedin)){
            $this->resume_linkedin = Storage::temporaryUrl($user->resume_linkedin, $this->expires_link);
        }

    }

    public function getConnectionName(): ?string
    {
        return 'rabbitmq_producer';
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        // Do nothing here.
    }
}
