<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class ResetPasswordRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'otp' => 'required|exists:password_reset_otps,otp|min:6|max:6',
            'password' => 'required|string|min:8|max:64',
            'password_confirm' => 'required|string|min:8|max:64|same:password',
        ];
    }
}
