<?php

namespace App\Http\Controllers\Api;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use Exception;
use Illuminate\Http\Request;
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
                return ResponseData::error('Invalid credentials', 'Email or password is incorrect', 401);
            }

            $user = auth()->user();
            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('Login successful', [
                'token' => $token,
                'user'  => $user
            ]);

        }catch(Exception $e){
            return ResponseData::error('Login failed', $e->getMessage(), $e->getCode() ?: 500);
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
                'password' => bcrypt($request->password),
            ]);

            $token = $user->createToken('api-token')->plainTextToken;

            return ResponseData::success('User registered successfully', [
                'token' => $token,
                'user'  => $user
            ], 201);
        }catch(ValidationException $e){
            return ResponseData::error('Validation failed', ['errors' => $e->errors()], 422);
        }catch(Exception $e){
            return ResponseData::error('Registration failed', ['error' => $e->getMessage()], $e->getCode() ?: 500);
        }

    }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();
        return ResponseData::success('Logged out successfully');
    }

    public function user(Request $request)
    {
        return ResponseData::success('User retrieved successfully', [
            'user' => $request->user()
        ]);
    }

}
