<?php 

it('can verify otp', function () {

    $user = authUser();

    \App\Models\PasswordResetOtp::create([
        'user_id' => $user->id,
        'otp' => 123456,
        'expires_at' => now()->addMinutes(10),
    ]);

    $response = $this->postJson('/api/auth/verify-otp', [
        'otp' => 123456
    ]);

    $response->assertOk();
});