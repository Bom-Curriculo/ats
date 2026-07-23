<?php

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;

uses(RefreshDatabase::class);

it('registers a user and stores their data correctly', function () {
    $userData = [
        'name' => 'lucas santos',
        'email' => 'lucassantos@gmail.com',
        'password' => 'password1234',
    ];
    $response = $this->postJson('/api/auth/register', [
        'name' => $userData['name'],
        'email' => $userData['email'],
        'password' => $userData['password'],
        'password_confirm' => $userData['password'],
    ]);

    $response
        ->assertStatus(201)
        ->assertJsonStructure([
            'code',
            'message',
            'data' => [
                'token',
                'user',
            ],
        ]);

    $this->assertDatabaseHas('users', [
        'email' => $userData['email'],
        'name' => $userData['name'],
    ]);
    $user = User::where('email', $userData['email'])->firstOrFail();

    expect(
        Hash::check($userData['password'], $user->password)
    )->toBeTrue();
});

describe('registration validation errors', function () {
    it('returns status 422 when the email is already registered', function () {
        $password = 'senha12345';
        $user = authUser([
            'email' => 'lucas@gmail.com',
            'password' => Hash::make($password),
        ]);
        $response = $this->postJson('/api/auth/register', [
            'name' => 'Test User',
            'email' => $user->email,
            'password' => $password,
            'password_confirm' => $password,
        ]);

        $response
            ->assertStatus(422)
            ->assertJsonPath(
                'data.errors.email.0',
                'The email has already been taken.'
            );

        expect(
            User::where('email', $user->email)->count()
        )->toBe(1);
    });
    it('returns status 422 when the email is empty', function () {
        $password = 'senha12345';
        $email = '';
        $response = $this->postJson('/api/auth/register', [
            'name' => 'Test User',
            'email' => $email,
            'password' => $password,
            'password_confirm' => $password,
        ]);

        $response
            ->assertStatus(422);
        $response->assertJsonPath(
            'data.errors.email.0',
            'The email field is required.'
        );
    });
    it('returns status 422 when the password is empty', function () {
        $password = '';
        $email = 'lucas@gmail.com';
        $response = $this->postJson('/api/auth/register', [
            'name' => 'Test User',
            'email' => $email,
            'password' => $password,
            'password_confirm' => $password,
        ]);

        $response
            ->assertStatus(422);
        $response->assertJsonPath(
            'data.errors.password.0',
            'The password field is required.'
        );
    });
});

describe('FCM token', function () {
    it('creates a device when the FCM token is provided', function () {
        $password = 'senha-correta';
        $email = 'lucas@gmail.com';
        $fcmToken = 'token-fcm-123';
        $response = $this->postJson('/api/auth/register', [
            'name' => 'lucas',
            'email' => $email,
            'password' => $password,
            'fcm' => $fcmToken,
            'password_confirm' => $password,
        ]);

        $response->assertJson([
            'message' => 'User registered successfully',
        ]);

        $this->assertDatabaseHas('user_devices', [
            'fcm_token' => 'token-fcm-123',
        ]);
    });
    it('does not create a device when FCM is not provided', function () {
        $password = 'senha-correta';
        $email = 'lucas@gmail.com';

        $response = $this->postJson('/api/auth/register', [
            'name' => 'lucas',
            'email' => $email,
            'password' => 'senha-correta',
            'password_confirm' => $password,
        ]);

        $response->assertJson([
            'message' => 'User registered successfully',
        ]);

        $user = User::where('email', $email)->firstOrFail();

        expect(
            $user->devices()->count()
        )->toBe(0);
    });
});