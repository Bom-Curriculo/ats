<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class ResetPasswordRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'otp' => 'required|exists:password_reset_otps,otp',
            'password' => 'required|string|min:8',
        ];
    }
}
