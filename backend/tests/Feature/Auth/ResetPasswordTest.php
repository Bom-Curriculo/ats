<?php

use App\Models\PasswordResetOtp;
use Illuminate\Support\Facades\Hash;

it('resets the password with a valid, already-verified otp', function () {

    $user = authUser([
        'password' => Hash::make('senha-antiga'),
    ]);

    PasswordResetOtp::create([
        'user_id' => $user->id,
        'otp' => 123456,
        'expires_at' => now()->addMinutes(10),
        'used_at' => now(),
    ]);

    $response = $this->postJson('/api/auth/reset-password', [
        'otp' => 123456,
        'password' => 'senha-nova-123',
        'password_confirm' => 'senha-nova-123',
    ]);

    $response->assertOk()
        ->assertJson([
            'message' => 'Password reset successfully',
        ]);

    expect(Hash::check('senha-nova-123', $user->fresh()->password))->toBeTrue();

    $this->assertDatabaseMissing('password_reset_otps', [
        'otp' => 123456,
    ]);
});

it('returns 500 when the otp was never verified', function () {

    $user = authUser();

    PasswordResetOtp::create([
        'user_id' => $user->id,
        'otp' => 654321,
        'expires_at' => now()->addMinutes(10),
    ]);

    $response = $this->postJson('/api/auth/reset-password', [
        'otp' => 654321,
        'password' => 'senha-nova-123',
        'password_confirm' => 'senha-nova-123',
    ]);

    $response->assertServerError();
});

it('returns 422 when passwords do not match', function () {

    $user = authUser();

    PasswordResetOtp::create([
        'user_id' => $user->id,
        'otp' => 111111,
        'expires_at' => now()->addMinutes(10),
        'used_at' => now(),
    ]);

    $response = $this->postJson('/api/auth/reset-password', [
        'otp' => 111111,
        'password' => 'senha-nova-123',
        'password_confirm' => 'senha-diferente',
    ]);

    $response->assertUnprocessable();
});
