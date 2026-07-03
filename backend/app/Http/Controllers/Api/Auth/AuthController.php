<?php

namespace App\Http\Controllers\Api\Auth;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Mail\UserResetPasswordMail;
use App\Models\PasswordResetOtp;
use App\Models\User;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{

    public function login(Request $request)
    {

        try{

            $request->validate([
                'email' => 'required|email',
                'password' => 'required',
            ]);

            if (!auth()->attempt($request->only('email', 'password'))) {
                return ResponseData::error('Invalid credentials', ['Email or password is incorrect'], 401);
            }

            $user = auth()->user();
            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('Login successful', [
                'token' => $token,
                'user'  => $user
            ]);

        }catch(Exception $e){
            return ResponseData::error('Login failed', [$e->getMessage()], 500);
        }
        
    }

    public function register(Request $request)
    {

        try{

            $request->validate([
                'name' => 'required|string|max:255',
                'email' => 'required|email|unique:users,email',
                'password' => 'required|string|min:8',
                'password_confirm' => 'required|string|same:password',
            ]);

            $user = \App\Models\User::create([
                'name' => $request->name,
                'email' => $request->email,
                'password' => Hash::make($request->password),
            ]);

            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('User registered successfully', [
                'token' => $token,
                'user'  => $user
            ], 201);
        }catch(ValidationException $e){
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        }catch(Exception $e){
            return ResponseData::error('Registration failed', ['error' => $e->getMessage()], 500);
        }

    }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();
        return ResponseData::success('Logged out successfully');
    }

    public function forgotPassword(Request $request)
    {
        try{

            $request->validate([
                'email' => 'required|email|exists:users,email',
            ]);

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
                'expires_at' => $expiresAt
            ]);

            Mail::to($user->email)
                    ->send(new UserResetPasswordMail($user, $otp));

            return ResponseData::success('OTP sent successfully to the provided email', [
                'expires_at' => $expiresAt
            ]);

        }catch(ValidationException $e){
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        }catch(Exception $e){
            return ResponseData::error('Forgot password failed', ['error' => $e->getMessage()], 500);
        }
    }

    public function verifyOtp(Request $request)
    {
        try{

            $request->validate([
                'otp' => 'required|digits:6|exists:password_reset_otps,otp'
            ]);

            $otpRecord = PasswordResetOtp::where('otp', $request->otp)
                ->where('otp', $request->otp)
                ->where('expires_at', '>', now())
                ->whereNull('used_at')
                ->first();

            if (!$otpRecord) {
                return ResponseData::error('Invalid or expired OTP', ['error' => 'The provided OTP is either invalid or has expired.'], 400);
            }

            // Mark the OTP as used
            $otpRecord->update(['used_at' => now()]);

            return ResponseData::success('Valid', [
                'message' => 'OTP is valid and has been marked as used.',
                'user_id' => $otpRecord->user_id
            ]);

        }catch(ValidationException $e){
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        }catch(Exception $e){
            return ResponseData::error('OTP verification failed', ['error' => $e->getMessage()], 500);
        }
    }

    public function resetPassword(Request $request)
    {

        try{

            $request->validate([
                'otp' => 'required|exists:password_reset_otps,otp',
                'password' => 'required|string|min:8',
            ]);

            $otp = PasswordResetOtp::where('otp', $request->otp)
                ->where('expires_at', '>', now())
                ->whereNotNull('used_at')
                ->first();

            $user = User::find($otp->user_id);
            $user->update(['password' => Hash::make($request->password)]);

            $otp->delete();

            return ResponseData::success('Password reset successfully', [
                'message' => 'Your password has been reset successfully.'
            ]);

        }catch(ValidationException $e){
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        }catch(Exception $e){
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
                'languages'
            ])->where('id', $request->user()->id)->first()
        ]);
    }

}
