<?php

use App\Http\Controllers\Api\Auth\AuthController;
use App\Http\Controllers\Api\Resume\ResumeController;
use App\Http\Controllers\Api\User\UserController;
use App\Services\RabbitMQ\Resume\ProducerResumesService;
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
    Route::middleware('auth:sanctum')->get('/logout', [AuthController::class, 'logout']);
});

// Only authenticated users can access the group routes bellow
Route::group([

    'middleware' => 'auth:sanctum',
    'prefix'     => 'client'

], function () {

    Route::prefix('/user')->group(function(){
    
        Route::get('/', [AuthController::class, 'user']);
        Route::put('/update', [UserController::class, 'update']);

    });

    Route::prefix('/resumes')->group(function(){

        Route::get('/files', [ResumeController::class, 'getResumesFiles']);
        Route::post('/validate-resume', [ResumeController::class, 'storeValidateResume']);
        Route::get('/pendings', [ResumeController::class, 'pendingResumes']);
        Route::get('/pendings/{resume}', [ResumeController::class, 'showPendingResume']);

    });

    Route::prefix('/services')->group(function(){

        Route::prefix('/rabbitmq')->group(function(){

            Route::post('/process', ProducerResumesService::class);

        });
    });
   
});
