<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class RegisterRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'name' => 'required|string|max:128|min:3',
            'email' => 'required|email|unique:users,email|min:5|max:128',
            'password' => 'required|string|min:8|max:64',
            'password_confirm' => 'required|string|same:password|min:8|max:64',
        ];
    }
}
