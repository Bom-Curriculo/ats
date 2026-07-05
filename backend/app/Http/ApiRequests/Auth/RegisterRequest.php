<?php

namespace App\Http\ApiRequests\Auth;

use App\Http\ApiRequests\CustomRequest;

class RegisterRequest extends CustomRequest
{
    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users,email',
            'password' => 'required|string|min:8',
            'password_confirm' => 'required|string|same:password',
        ];
    }
}
