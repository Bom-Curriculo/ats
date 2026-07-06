<?php

namespace App\Jobs\Api\RabbitMQ\Resumes;

use App\Models\ResumeAnalytic;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;
use Throwable;

class ResumeProcessingConsumer implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public array $resume
    )
    {
        //
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        ResumeAnalytic::create($this->resume['resume'] ?? $this->resume);
    }

    public function failed(Throwable $exception): void
    {
        Log::channel('rabbit_resumes')->error('Job ResumeProcessingConsumer failed definitively', [
            'exception' => $exception->getMessage(),
            'payload' => $this->resume,
            'trace' => $exception->getTraceAsString()
        ]);
    }
}
