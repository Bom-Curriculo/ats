<?php

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

it('uploads cv and linkedin files and creates a resume record', function () {

    Storage::fake('local');

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/resumes/new-resume', [
            'resume_cv' => UploadedFile::fake()->create('cv.pdf', 100),
            'resume_linkedin' => UploadedFile::fake()->create('linkedin.pdf', 100),
            'github_link' => 'https://github.com/pedroaruana',
            'site_link' => 'https://pedroaruana.dev',
        ]);

    $response->assertOk()
        ->assertJson([
            'message' => 'User Updated',
        ]);

    $user = $auth['user']->fresh();
    expect($user->github_link)->toBe('https://github.com/pedroaruana')
        ->and($user->site_link)->toBe('https://pedroaruana.dev')
        ->and($user->resume_cv)->not->toBeNull()
        ->and($user->resume_linkedin)->not->toBeNull();

    Storage::disk('local')->assertExists($user->resume_cv);

    $this->assertDatabaseHas('user_resumes', [
        'user_id' => $user->id,
    ]);
});

it('processes the skills sent along with the resume', function () {

    Storage::fake('local');

    $auth = actingAsUser();

    $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/resumes/new-resume', [
            'skills' => [
                ['name' => 'PHP'],
                ['name' => 'Laravel'],
            ],
        ])
        ->assertOk();

    expect($auth['user']->skills()->pluck('name')->all())->toBe(['PHP', 'Laravel']);
});

it('works with only links, no files', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/resumes/new-resume', [
            'github_link' => 'https://github.com/pedroaruana',
        ]);

    $response->assertOk();

    $this->assertDatabaseMissing('user_resumes', [
        'user_id' => $auth['user']->id,
    ]);
});

it('requires authentication', function () {

    $this->postJson('/api/client/resumes/new-resume')
        ->assertUnauthorized();
});
