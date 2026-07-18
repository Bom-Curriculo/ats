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

class AuthController extends Controller
{
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

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        if ($request->filled('fcm')) {
            UserDevice::query()->where('fcm_token', $request->fcm)->delete();
        }

        return ResponseData::success('Logged out successfully');
    }

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
