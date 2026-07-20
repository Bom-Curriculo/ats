<?php

namespace App\Http\Controllers\Api\Auth;

use App\Helpers\ResponseData;
use App\Http\ApiRequests\Auth\ForgotPasswordRequest;
use App\Http\ApiRequests\Auth\LoginRequest;
use App\Http\ApiRequests\Auth\RegisterRequest;
use App\Http\ApiRequests\Auth\ResetPasswordRequest;
use App\Http\ApiRequests\Auth\VerifyOtpRequest;
use App\Http\Controllers\Controller;
use App\Mail\UserResetPasswordMail;
use App\Models\PasswordResetOtp;
use App\Models\User;
use App\Models\UserDevice;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use Illuminate\Validation\ValidationException;
use OpenApi\Attributes as OAT;

class AuthController extends Controller
{
    #[OAT\Post(
        path: '/auth/login',
        summary: 'Autentica um usuário',
        security: [],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: true,
            content: new OAT\JsonContent(
                required: ['email', 'password'],
                properties: [
                    new OAT\Property(property: 'email', type: 'string', format: 'email', example: 'user@example.com'),
                    new OAT\Property(property: 'password', type: 'string', format: 'password', example: 'secret123'),
                    new OAT\Property(property: 'fcm', type: 'string', nullable: true, description: 'Token FCM do dispositivo, para notificações push'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Login realizado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Login successful'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'token', type: 'string'),
                                new OAT\Property(property: 'user', type: 'object'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(
                response: 401,
                description: 'Credenciais inválidas',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 401),
                        new OAT\Property(property: 'message', type: 'string', example: 'Invalid credentials'),
                        new OAT\Property(property: 'data', type: 'array', items: new OAT\Items(type: 'string'), example: ['Email or password is incorrect']),
                    ]
                )
            ),
            new OAT\Response(response: 422, description: 'Erro de validação', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao autenticar',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Login failed'),
                        new OAT\Property(property: 'data', type: 'array', items: new OAT\Items(type: 'string'), example: ['SQLSTATE[HY000]...']),
                    ]
                )
            ),
        ]
    )]
    public function login(LoginRequest $request)
    {
        try {

            $user = User::query()->where('email', $request->email)->first();

            if (! $user || ! Hash::check($request->password, $user->password)) {
                return ResponseData::error('Invalid credentials', ['Email or password is incorrect'], 401);
            }

            if ($request->filled('fcm')) {
                $fcm = $user->devices()->where('fcm_token', $request->fcm)->exists();
                if (! $fcm) {
                    $user->devices()->create([
                        'fcm_token' => $request->fcm,
                    ]);
                }
            }

            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('Login successful', [
                'token' => $token,
                'user' => $user,
            ]);

        } catch (Exception $e) {

            return ResponseData::error('Login failed', [$e->getMessage()], 500);

        }
    }

    #[OAT\Post(
        path: '/auth/register',
        summary: 'Registra um novo usuário',
        security: [],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: true,
            content: new OAT\JsonContent(
                required: ['name', 'email', 'password', 'password_confirm'],
                properties: [
                    new OAT\Property(property: 'name', type: 'string', example: 'João da Silva'),
                    new OAT\Property(property: 'email', type: 'string', format: 'email', example: 'user@example.com'),
                    new OAT\Property(property: 'password', type: 'string', format: 'password', example: 'secret123'),
                    new OAT\Property(property: 'password_confirm', type: 'string', format: 'password', example: 'secret123'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 201,
                description: 'Usuário registrado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 201),
                        new OAT\Property(property: 'message', type: 'string', example: 'User registered successfully'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'token', type: 'string'),
                                new OAT\Property(property: 'user', type: 'object'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 422, description: 'Erro de validação (e-mail já em uso, senhas não conferem, etc.)', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao registrar',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Registration failed'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function register(RegisterRequest $request)
    {

        try {
            $user = User::create([
                'name' => $request->name,
                'email' => $request->email,
                'password' => Hash::make($request->password),
            ]);

            if ($request->filled('fcm')) {
                $fcm = $user->devices()->where('fcm_token', $request->fcm)->exists();
                if (! $fcm) {
                    $user->devices()->create([
                        'fcm_token' => $request->fcm,
                    ]);
                }
            }

            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('User registered successfully', [
                'token' => $token,
                'user' => $user,
            ], 201);
        } catch (ValidationException $e) {
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        } catch (Exception $e) {
            return ResponseData::error('Registration failed', ['error' => $e->getMessage()], 500);
        }

    }

    #[OAT\Post(
        path: '/auth/logout',
        summary: 'Encerra a sessão do usuário autenticado',
        security: [['bearerAuth' => []]],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: false,
            content: new OAT\JsonContent(
                properties: [
                    new OAT\Property(property: 'fcm', type: 'string', nullable: true, description: 'Token FCM do dispositivo a ser removido'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Logout realizado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Logged out successfully'),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
        ]
    )]
    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        if ($request->filled('fcm')) {
            UserDevice::query()->where('fcm_token', $request->fcm)->delete();
        }

        return ResponseData::success('Logged out successfully');
    }

    #[OAT\Post(
        path: '/auth/forgot-password',
        summary: 'Envia um código OTP por e-mail para redefinição de senha',
        security: [],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: true,
            content: new OAT\JsonContent(
                required: ['email'],
                properties: [
                    new OAT\Property(property: 'email', type: 'string', format: 'email', example: 'user@example.com'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'OTP enviado com sucesso para o e-mail informado',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'OTP sent successfully to the provided email'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'expires_at', type: 'string', format: 'date-time'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 422, description: 'E-mail não encontrado ou inválido', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao processar a solicitação',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Forgot password failed'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function forgotPassword(ForgotPasswordRequest $request)
    {
        try {
            $user = User::where('email', $request->email)->first();

            PasswordResetOtp::query()
                ->where('user_id', $user->id)
                ->orWhere('expires_at', '<', now())
                ->delete();

            $otp = rand(100000, 999999);
            $expiresAt = now()->addMinutes(15);

            PasswordResetOtp::create([
                'user_id' => $user->id,
                'otp' => $otp,
                'expires_at' => $expiresAt,
            ]);

            Mail::to($user->email)
                ->send(new UserResetPasswordMail($user, $otp));

            return ResponseData::success('OTP sent successfully to the provided email', [
                'expires_at' => $expiresAt,
            ]);

        } catch (ValidationException $e) {
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        } catch (Exception $e) {
            return ResponseData::error('Forgot password failed', ['error' => $e->getMessage()], 500);
        }
    }

    #[OAT\Post(
        path: '/auth/verify-otp',
        summary: 'Verifica se um código OTP é válido',
        security: [],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: true,
            content: new OAT\JsonContent(
                required: ['otp'],
                properties: [
                    new OAT\Property(property: 'otp', type: 'string', example: '123456', description: 'Código de 6 dígitos enviado por e-mail'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'OTP válido',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Valid'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'message', type: 'string'),
                                new OAT\Property(property: 'user_id', type: 'integer'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(
                response: 400,
                description: 'OTP inválido ou expirado',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 400),
                        new OAT\Property(property: 'message', type: 'string', example: 'Invalid or expired OTP'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string', example: 'The provided OTP is either invalid or has expired.')]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 422, description: 'Erro de validação', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao verificar o OTP',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'OTP verification failed'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function verifyOtp(VerifyOtpRequest $request)
    {
        try {

            $otpRecord = PasswordResetOtp::where('otp', $request->otp)
                ->where('otp', $request->otp)
                ->where('expires_at', '>', now())
                ->whereNull('used_at')
                ->first();

            if (! $otpRecord) {
                return ResponseData::error('Invalid or expired OTP', ['error' => 'The provided OTP is either invalid or has expired.'], 400);
            }

            // Mark the OTP as used
            $otpRecord->update(['used_at' => now()]);

            return ResponseData::success('Valid', [
                'message' => 'OTP is valid and has been marked as used.',
                'user_id' => $otpRecord->user_id,
            ]);

        } catch (ValidationException $e) {
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        } catch (Exception $e) {
            return ResponseData::error('OTP verification failed', ['error' => $e->getMessage()], 500);
        }
    }

    #[OAT\Post(
        path: '/auth/reset-password',
        summary: 'Redefine a senha do usuário usando um OTP já verificado',
        security: [],
        tags: ['Auth'],
        requestBody: new OAT\RequestBody(
            required: true,
            content: new OAT\JsonContent(
                required: ['otp', 'password', 'password_confirm'],
                properties: [
                    new OAT\Property(property: 'otp', type: 'string', example: '123456'),
                    new OAT\Property(property: 'password', type: 'string', format: 'password', example: 'newSecret123'),
                    new OAT\Property(property: 'password_confirm', type: 'string', format: 'password', example: 'newSecret123'),
                ]
            )
        ),
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Senha redefinida com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'Password reset successfully'),
                    ]
                )
            ),
            new OAT\Response(response: 422, description: 'Erro de validação (OTP inválido, senhas não conferem, etc.)', content: new OAT\JsonContent(ref: '#/components/schemas/ValidationErrorResponse')),
            new OAT\Response(
                response: 500,
                description: 'Erro interno ao redefinir a senha',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 500),
                        new OAT\Property(property: 'message', type: 'string', example: 'Password reset failed'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [new OAT\Property(property: 'error', type: 'string')]
                        ),
                    ]
                )
            ),
        ]
    )]
    public function resetPassword(ResetPasswordRequest $request)
    {

        try {

            $otp = PasswordResetOtp::where('otp', $request->otp)
                ->where('expires_at', '>', now())
                ->whereNotNull('used_at')
                ->first();

            $user = User::find($otp->user_id);
            $user->update(['password' => Hash::make($request->password)]);

            $otp->delete();

            return ResponseData::success('Password reset successfully', [
                'message' => 'Your password has been reset successfully.',
            ]);

        } catch (ValidationException $e) {
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        } catch (Exception $e) {
            return ResponseData::error('Password reset failed', ['error' => $e->getMessage()], 500);
        }

    }

    #[OAT\Get(
        path: '/client/user',
        summary: 'Retorna os dados do usuário autenticado',
        security: [['bearerAuth' => []]],
        tags: ['Auth'],
        responses: [
            new OAT\Response(
                response: 200,
                description: 'Usuário retornado com sucesso',
                content: new OAT\JsonContent(
                    properties: [
                        new OAT\Property(property: 'code', type: 'integer', example: 200),
                        new OAT\Property(property: 'message', type: 'string', example: 'User retrieved successfully'),
                        new OAT\Property(
                            property: 'data',
                            type: 'object',
                            properties: [
                                new OAT\Property(property: 'user', type: 'object'),
                            ]
                        ),
                    ]
                )
            ),
            new OAT\Response(response: 401, description: 'Não autenticado', content: new OAT\JsonContent(ref: '#/components/schemas/UnauthenticatedResponse')),
        ]
    )]
    public function user(Request $request)
    {
        return ResponseData::success('User retrieved successfully', [
            'user' => User::with([
                'skills',
                'experiences',
                'qualifications',
                'languages',
                'projects',
            ])->where('id', $request->user()->id)->first(),
        ]);
    }
}
