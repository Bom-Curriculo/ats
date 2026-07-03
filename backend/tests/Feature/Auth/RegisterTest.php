<?php

it('can register a user', function () {

    $response = $this->postJson('/api/auth/register', [
        'name' => 'Test User',
        'email' => 'test@example.com',
        'password' => 'password123',
        'password_confirm' => 'password123',
    ]);

    $response->assertStatus(201);
});