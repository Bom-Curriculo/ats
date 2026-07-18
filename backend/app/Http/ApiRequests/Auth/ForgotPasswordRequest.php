<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class ForgotPasswordRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'email' => 'required|email|exists:users,email|min:5|max:128',
        ];
    }
}
