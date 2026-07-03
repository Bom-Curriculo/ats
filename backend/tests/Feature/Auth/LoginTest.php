<?php 

it('can login successfully', function () {

    $user = authUser([
        'password' => bcrypt('password')
    ]);

    $response = $this->postJson('/api/auth/login', [
        'email' => $user->email,
        'password' => 'password'
    ]);

    $response->assertOk()
        ->assertJsonStructure([
            'code',
            'message',
            'data' => [
                'token',
                'user'
            ]
        ]);
});