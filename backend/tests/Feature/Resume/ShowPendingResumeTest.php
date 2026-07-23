<?php

it('shows a resume analytic belonging to the authenticated user', function () {

    $auth = actingAsUser();

    $analytic = $auth['user']->resumeAnalytics()->create([
        'status' => 'pending',
    ]);

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson("/api/client/resumes/pendings/{$analytic->id}");

    $response->assertOk()
        ->assertJson([
            'data' => [
                'id' => $analytic->id,
            ],
        ]);
});

it('returns 404 for a resume analytic belonging to another user', function () {

    $auth = actingAsUser();
    $otherUser = authUser();

    $analytic = $otherUser->resumeAnalytics()->create([
        'status' => 'pending',
    ]);

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson("/api/client/resumes/pendings/{$analytic->id}");

    $response->assertNotFound();
});

it('returns 404 for a nonexistent resume analytic', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson('/api/client/resumes/pendings/999999');

    $response->assertNotFound();
});

it('requires authentication', function () {

    $this->getJson('/api/client/resumes/pendings/1')
        ->assertUnauthorized();
});
