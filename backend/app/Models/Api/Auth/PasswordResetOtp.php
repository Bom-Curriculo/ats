<?php

namespace App\Models\Api\Auth;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Casts;

#[Fillable(['user_id', 'otp', 'expires_at', 'used_at'])]
#[Casts(['expires_at' => 'datetime', 'used_at' => 'datetime'])]
class PasswordResetOtp extends Model
{
    //
}
