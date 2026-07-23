<?php

use App\Models\SystemUser;

test('login screen can be rendered', function () {
    $response = $this->get('/login');

    $response->assertStatus(200);
});

test('users can authenticate using the login screen', function () {
    $user = SystemUser::factory()->create();

    $response = $this->post('/login', [
        'email' => $user->email,
        'password' => 'password',
    ]);

    $this->assertAuthenticated('system');
    $response->assertRedirect(route('dashboard', absolute: false));
});

test('users can not authenticate with invalid password', function () {
    $user = SystemUser::factory()->create();

    $this->post('/login', [
        'email' => $user->email,
        'password' => 'wrong-password',
    ]);

    $this->assertGuest('system');
});

test('users can logout', function () {
    $user = SystemUser::factory()->create();

    $response = $this->actingAs($user, 'system')->post('/logout');

    $this->assertGuest('system');
    $response->assertRedirect('/');
});
