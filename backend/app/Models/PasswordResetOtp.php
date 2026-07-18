<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['user_id', 'otp', 'expires_at', 'used_at'])]
class PasswordResetOtp extends Model
{
    public $casts = [
        'expires_at' => 'datetime',
        'used_at' => 'datetime',
    ];
}
