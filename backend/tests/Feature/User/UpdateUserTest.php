<?php

it('updates user profile', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->putJson('/api/client/user/update', [
            'name' => 'New Name',
            'city' => 'São Paulo'
        ]);

    $response->assertOk();

    expect($auth['user']->fresh()->name)->toBe('New Name');
});