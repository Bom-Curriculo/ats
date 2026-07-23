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
                'min:5',
                'max:128',
            ],
            'password' => [
                'required',
                'string',
                'min:8',
                'max:64',
            ],
            'fcm' => ['nullable', 'string'],
        ];
    }
}
