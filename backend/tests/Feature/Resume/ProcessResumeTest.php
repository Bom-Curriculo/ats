<?php

use App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher;
use Illuminate\Support\Facades\Queue;

it('dispatches the resume processing job for the authenticated user', function () {

    Queue::fake();

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/services/rabbitmq/process');

    $response->assertOk()
        ->assertJson([
            'message' => 'Success',
        ]);

    Queue::assertPushed(ResumeProcessingPublisher::class, function ($job) use ($auth) {
        return $job->user_id === $auth['user']->id;
    });
});

it('requires authentication', function () {

    $this->postJson('/api/client/services/rabbitmq/process')
        ->assertUnauthorized();
});

it('currently breaks with a server error when user_resume_id is sent', function () {

    // Known bug (not fixed here, only documented): the controller passes the raw
    // id straight into ResumeProcessingPublisher's constructor, which type-hints
    // ?UserResume, not an id. This test locks in the current (broken) behavior so
    // a future fix is a visible, intentional test change instead of a silent one.
    Queue::fake();

    $auth = actingAsUser();
    $resume = $auth['user']->resumes()->create([
        'original_file_path_cv' => 'resumes/cv.pdf',
    ]);

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/services/rabbitmq/process', [
            'user_resume_id' => $resume->id,
        ]);

    $response->assertServerError();
});
