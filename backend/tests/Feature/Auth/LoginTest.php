<?php
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;

uses(RefreshDatabase::class);

it('can login successfully', function () {

    $user = authUser([
        'password' => bcrypt('password'),
    ]);

    $response = $this->postJson('/api/auth/login', [
        'email' => $user->email,
        'password' => 'password',
    ]);

    $response->assertOk()
        ->assertJsonStructure([
        'code',
        'message',
        'data' => [
            'token',
            'user',
        ],
    ]);
});

describe('invalid cretentials',function(){
    it('returns status 401 when the password is incorrect', function () {
        $user = authUser([
            'email' => 'usuario@email.com',
            'password' => Hash::make('senha-correta'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => 'usuario@email.com',
            'password' => 'senha-incorreta',
        ]);

        $response
            ->assertUnauthorized()
            ->assertJson([
                'message' => 'Invalid credentials',
            ])
        ->assertJsonMissingPath('token');

        $this->assertDatabaseMissing('user_devices', [
            'user_id' => $user->id,
        ]);
    });
    it('returns status 401 when the email does not exist', function () {
        $response = $this->postJson('/api/auth/login', [
            'email' => 'lucas@gmail.com',
            'password' => 'senha-incorreta',
        ]);

        $response
            ->assertUnauthorized()
            ->assertJson([
                'message' => 'Invalid credentials',
            ])
        ->assertJsonMissingPath('token');

    });
    it('returns status 422 when email is missing', function () {
        $response = $this->postJson('/api/auth/login', [
            'password' => 'senha',
        ]);

        $response
            ->assertUnprocessable()
            ->assertJsonStructure([
                'code',
                'message',
                'data' => [
                    'errors' => [
                        'email',
                    ],
                ],
            ]);
    });

    it('returns status 422 when password is missing', function () {
        $response = $this->postJson('/api/auth/login', [
            'email' => 'test@gmail.com',
        ]);

        $response
            ->assertUnprocessable()
            ->assertJsonStructure([
                'code',
                'message',
                'data' => [
                    'errors' => [
                        'password',
                    ],
                ],
            ]);
    });
});



describe('FCM token',function(){
    it('creates a device when the fcm token is new', function () {
        $user = authUser([
            'email' => 'usuario@email.com',
            'password' => Hash::make('senha-correta'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => $user->email,
            'password' => 'senha-correta',
            'fcm'=>'token-fcm-123'
        ]);

        $response->assertJson([
            'message' => 'Login successful',
        ]);

        $this->assertDatabaseHas('user_devices', [
            'user_id' => $user->id,
            'fcm_token' => 'token-fcm-123',
        ]);
    });
    it('does not create a device when fcm is not provided', function () {
        $user = authUser([
            'email' => 'usuario@email.com',
            'password' => Hash::make('senha-correta'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => $user->email,
            'password' => 'senha-correta',
        ]);

        $response->assertJson([
            'message' => 'Login successful',
        ]);

        $this->assertDatabaseMissing('user_devices', [
            'user_id' => $user->id,
            'fcm_token' => 'token-fcm-123',
        ]);
    });
    it('does not duplicate an existing fcm token',function(){
        $fcmToken = 'token-fcm-123';
        $user = authUser([
            'email' => 'usuario@email.com',
            'password' => Hash::make('senha-correta'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => $user->email,
            'password' => 'senha-correta',
            'fcm'=>$fcmToken
        ]);

        $response->assertJson([
            'message' => 'Login successful',
        ]);
        $response2 = $this->postJson('/api/auth/login', [
            'email' => $user->email,
            'password' => 'senha-correta',
            'fcm'=>$fcmToken
        ]);

        $response2->assertJson([
            'message'=>'Login successful'
        ]);

        
        expect(
            $user->devices()->where('fcm_token',$fcmToken)
            ->count()
        )->toBe(1);
    });

});