<?php

use App\Http\Controllers\System\ProfileController;
use App\Models\User;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return redirect()->route('login');
});

Route::get('/dashboard', function () {
    return view('system.dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth:system')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');

    Route::get('/users', function(){
        return view('system.pages.users.index', [
            'users' => User::orderByDesc('created_at')->get(),
        ]);
    })->name('users');

    Route::get('/resumes', function(){
        
    })->name('resumes');

});

require __DIR__.'/auth.php';