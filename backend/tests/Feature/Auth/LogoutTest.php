<?php

use App\Models\UserDevice;

it('revokes the current access token', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/auth/logout');

    $response->assertOk()
        ->assertJson([
            'message' => 'Logged out successfully',
        ]);

    expect($auth['user']->fresh()->tokens()->count())->toBe(0);
});

it('removes the device matching the given fcm token', function () {

    $auth = actingAsUser();

    UserDevice::create([
        'user_id' => $auth['user']->id,
        'fcm_token' => 'token-fcm-123',
    ]);

    $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/auth/logout', [
            'fcm' => 'token-fcm-123',
        ])
        ->assertOk();

    $this->assertDatabaseMissing('user_devices', [
        'user_id' => $auth['user']->id,
        'fcm_token' => 'token-fcm-123',
    ]);
});

it('requires authentication', function () {

    $this->postJson('/api/auth/logout')
        ->assertUnauthorized();
});
