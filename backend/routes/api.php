<?php

use App\Http\Controllers\Api\Auth\AuthController;
use App\Http\Controllers\Api\User\UserController;
use Illuminate\Support\Facades\Route;

// Unauthenticated routes
Route::group([
    'prefix' => 'auth'
], function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::post('/register', [AuthController::class, 'register']);
    Route::post('/forgot-password', [AuthController::class, 'forgotPassword']);
    Route::post('/verify-otp', [AuthController::class, 'verifyOtp']);
    Route::post('/reset-password', [AuthController::class, 'resetPassword']);
    Route::middleware('auth:sanctum')->post('/logout', [AuthController::class, 'logout']);
});

// Only authenticated users can access the group routes bellow
Route::group([
    'middleware' => 'auth:sanctum',
    'prefix'     => 'client'
], function () {
    Route::get('/user', [AuthController::class, 'user']);
    Route::post('/validate-resume', [UserController::class, 'storeValidateResume']);
    Route::get('/resume-files/{type?}', [UserController::class, 'getResumesFiles']);
    Route::put('/user/update', [UserController::class, 'update']);
});
