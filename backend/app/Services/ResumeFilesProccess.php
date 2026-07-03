<?php

namespace App\Services;

use App\Jobs\ProccessResumesJobs;
use App\Models\User;

class ResumeFilesProccess {

    public static function handle(User $user)
    {
        ProccessResumesJobs::dispatch($user)->onConnection('rabbitmq');
    }

}