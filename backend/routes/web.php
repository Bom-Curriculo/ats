<?php

use App\Jobs\ProccessResumesJobs;
use Illuminate\Support\Facades\Route;

Route::get('/', function(){
    return response()->json([
        'message' => 'Welcome to the ATS API, use the /api prefix to access the endpoints.',
        'version' => '1.0.0'
    ]);
});

Route::get('teste', function(){
    ProccessResumesJobs::dispatch(5, 'testeee')->onConnection('rabbitmq');
});