<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class LoginRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'email' => [
                'required',
                'email',
            ],
            'password' => [
                'required',
                'string',
            ],
        ];
    }
}