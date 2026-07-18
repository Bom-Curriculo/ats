<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class VerifyOtpRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'otp' => 'required|digits:6|exists:password_reset_otps,otp|min:6|max:6',
        ];
    }
}
