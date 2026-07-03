<?php

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(
    Tests\TestCase::class,
    RefreshDatabase::class,
)->in('Feature', 'Unit');

function authUser(array $attributes = []): User
{
    return User::factory()->create($attributes);
}

function actingAsUser(array $attributes = []): array
{
    $user = authUser($attributes);

    $token = $user->createToken('test-token')->plainTextToken;

    return [
        'user' => $user,
        'headers' => [
            'Authorization' => "Bearer {$token}",
            'Accept' => 'application/json',
        ],
    ];
}