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
use OpenApi\Attributes as OA;

#[OA\Tag(name: 'Auth', description: 'Autenticação e recuperação de senha')]
class AuthController extends Controller
{
    #[OA\Post(
        path: '/auth/login',
        tags: ['Auth'],
        summary: 'Login do usuário',
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['email', 'password'],
                properties: [
                    new OA\Property(property: 'email', type: 'string', format: 'email', example: 'user@example.com'),
                    new OA\Property(property: 'password', type: 'string', format: 'password', example: 'senha123'),
                    new OA\Property(property: 'fcm', type: 'string', nullable: true, description: 'Token de push notification do dispositivo'),
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'Login realizado com sucesso',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'token', type: 'string'),
                                new OA\Property(property: 'user', type: 'object'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 401, description: 'Credenciais inválidas', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
            new OA\Response(response: 422, description: 'Erro de validação', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Post(
        path: '/auth/register',
        tags: ['Auth'],
        summary: 'Cria uma nova conta',
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['name', 'email', 'password', 'password_confirm'],
                properties: [
                    new OA\Property(property: 'name', type: 'string', example: 'Pedro Aruanã'),
                    new OA\Property(property: 'email', type: 'string', format: 'email'),
                    new OA\Property(property: 'password', type: 'string', format: 'password'),
                    new OA\Property(property: 'password_confirm', type: 'string', format: 'password'),
                    new OA\Property(property: 'fcm', type: 'string', nullable: true),
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 201,
                description: 'Usuário criado',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'token', type: 'string'),
                                new OA\Property(property: 'user', type: 'object'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 422, description: 'Erro de validação (ex: email já cadastrado)', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Post(
        path: '/auth/logout',
        tags: ['Auth'],
        summary: 'Encerra a sessão atual (revoga o token)',
        security: [['sanctum' => []]],
        responses: [
            new OA\Response(response: 200, description: 'Logout realizado', content: new OA\JsonContent(ref: '#/components/schemas/ApiSuccessResponse')),
            new OA\Response(response: 401, description: 'Não autenticado'),
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

    #[OA\Post(
        path: '/auth/forgot-password',
        tags: ['Auth'],
        summary: 'Envia um código OTP por email pra iniciar a recuperação de senha',
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['email'],
                properties: [
                    new OA\Property(property: 'email', type: 'string', format: 'email', description: 'Precisa ser um email já cadastrado'),
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'OTP enviado',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'expires_at', type: 'string', format: 'date-time'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 422, description: 'Email não encontrado', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Post(
        path: '/auth/verify-otp',
        tags: ['Auth'],
        summary: 'Verifica o código OTP enviado por email',
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['otp'],
                properties: [
                    new OA\Property(property: 'otp', type: 'string', example: '123456', description: 'Código de 6 dígitos'),
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'OTP válido',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'message', type: 'string'),
                                new OA\Property(property: 'user_id', type: 'integer'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 400, description: 'OTP inválido ou expirado', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Post(
        path: '/auth/reset-password',
        tags: ['Auth'],
        summary: 'Define a nova senha após validar o OTP',
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['otp', 'password', 'password_confirm'],
                properties: [
                    new OA\Property(property: 'otp', type: 'string', example: '123456'),
                    new OA\Property(property: 'password', type: 'string', format: 'password'),
                    new OA\Property(property: 'password_confirm', type: 'string', format: 'password'),
                ]
            )
        ),
        responses: [
            new OA\Response(response: 200, description: 'Senha alterada com sucesso', content: new OA\JsonContent(ref: '#/components/schemas/ApiSuccessResponse')),
            new OA\Response(response: 422, description: 'OTP inválido/expirado ou senhas não conferem', content: new OA\JsonContent(ref: '#/components/schemas/ApiErrorResponse')),
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

    #[OA\Get(
        path: '/client/user',
        tags: ['Auth'],
        summary: 'Retorna os dados do usuário autenticado, com relações completas',
        security: [['sanctum' => []]],
        responses: [
            new OA\Response(
                response: 200,
                description: 'Usuário retornado com skills, experiences, qualifications, languages e projects',
                content: new OA\JsonContent(
                    allOf: [
                        new OA\Schema(ref: '#/components/schemas/ApiSuccessResponse'),
                        new OA\Schema(properties: [
                            new OA\Property(property: 'data', type: 'object', properties: [
                                new OA\Property(property: 'user', type: 'object'),
                            ]),
                        ]),
                    ]
                )
            ),
            new OA\Response(response: 401, description: 'Não autenticado'),
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
