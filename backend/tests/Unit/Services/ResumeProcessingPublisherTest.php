<?php

it('creates resume processing job with correct data', function () {

    $user = authUser([
        'resume_cv' => 'cv.pdf',
        'resume_linkedin' => 'linkedin.pdf',
    ]);

    $job = new \App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher($user);

    expect($job->user_id)->toBe($user->id);
});

use Illuminate\Support\Facades\Storage;

it('generates temporary urls for resumes', function () {

    Storage::fake('local');

    $user = authUser([
        'resume_cv' => 'resumes/cv.pdf',
    ]);

    $job = new \App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher($user);

    expect($job->resume_cv)->not->toBeNull();
});