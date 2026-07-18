<?php

it('returns authenticated user', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson('/api/client/user');

    $response->assertOk()
        ->assertJsonStructure([
            'data' => [
                'user',
            ],
        ]);
});
