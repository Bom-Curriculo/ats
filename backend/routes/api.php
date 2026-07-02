<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;

// Unauthenticated routes
Route::post('/login', [AuthController::class, 'login']);
Route::post('/register', [AuthController::class, 'register']);
Route::middleware('auth:sanctum')->post('/logout', [AuthController::class, 'logout']);

// Only authenticated users can access the group routes bellow
Route::group([
    'middleware' => 'auth:sanctum',
    'prefix'     => 'client'
], function () {
    Route::get('/user', [AuthController::class, 'user']);

});
