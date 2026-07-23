<?php

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

/*
|--------------------------------------------------------------------------
| Test Case
|--------------------------------------------------------------------------
|
| The closure you provide to your test functions is always bound to a specific PHPUnit test
| case class. By default, that class is "PHPUnit\Framework\TestCase". Of course, you may
| need to change it using the "pest()" function to bind a different classes or traits.
|
*/

pest()->extend(TestCase::class)
    ->use(RefreshDatabase::class)
    ->in('Feature', 'Unit');

/*
|--------------------------------------------------------------------------
| Expectations
|--------------------------------------------------------------------------
|
| When you're writing tests, you often need to check that values meet certain conditions. The
| "expect()" function gives you access to a set of "expectations" methods that you can use
| to assert different things. Of course, you may extend the Expectation API at any time.
|
*/

expect()->extend('toBeOne', function () {
    return $this->toBe(1);
});

/*
|--------------------------------------------------------------------------
| Functions
|--------------------------------------------------------------------------
|
| While Pest is very powerful out-of-the-box, you may have some testing code specific to your
| project that you don't want to repeat in every file. Here you can also expose helpers as
| global functions to help you to reduce the number of lines of code in your test files.
|
*/

/**
 * Cria um usuário (App\Models\User) para testes que só precisam do model,
 * sem autenticação via API (ex.: testes de trait/serviço que operam
 * diretamente sobre um usuário já existente). Aceita overrides de atributos,
 * repassados direto pra factory (ex.: authUser(['password' => bcrypt('x')])).
 *
 * @param  array<string, mixed>  $attributes
 */
function authUser(array $attributes = []): User
{
    return User::factory()->create($attributes);
}

/**
 * Cria um usuário e autentica via Sanctum, devolvendo o usuário e os
 * headers prontos para requests às rotas protegidas por auth:sanctum
 * (grupo /api/client/*). Aceita os mesmos overrides de atributos que authUser().
 *
 * @param  array<string, mixed>  $attributes
 * @return array{user: User, headers: array<string, string>}
 */
function actingAsUser(array $attributes = []): array
{
    $user = authUser($attributes);

    $token = $user->createToken('test-token')->plainTextToken;

    return [
        'user' => $user,
        'headers' => [
            'Authorization' => 'Bearer '.$token,
        ],
    ];
}
