<?php

it('can request password reset OTP', function () {

    $user = authUser();

    $response = $this->postJson('/api/auth/forgot-password', [
        'email' => $user->email
    ]);

    $response->assertOk();
});