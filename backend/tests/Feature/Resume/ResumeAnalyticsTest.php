<?php

it('lists the user resume analytics ordered from newest to oldest', function () {

    $auth = actingAsUser();

    $this->travelTo(now()->subDay());
    $older = $auth['user']->resumeAnalytics()->create([
        'status' => 'pending',
    ]);

    $this->travelBack();
    $newer = $auth['user']->resumeAnalytics()->create([
        'status' => 'pending',
    ]);

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson('/api/client/resumes/pendings');

    $response->assertOk();

    $ids = collect($response->json('data'))->pluck('id');
    expect($ids->first())->toBe($newer->id)
        ->and($ids->last())->toBe($older->id);
});

it('does not list analytics belonging to another user', function () {

    $auth = actingAsUser();
    $otherUser = authUser();

    $otherUser->resumeAnalytics()->create(['status' => 'pending']);

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson('/api/client/resumes/pendings');

    $response->assertOk()
        ->assertJsonCount(0, 'data');
});

it('requires authentication', function () {

    $this->getJson('/api/client/resumes/pendings')
        ->assertUnauthorized();
});
