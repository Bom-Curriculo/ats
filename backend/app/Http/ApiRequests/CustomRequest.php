<?php

namespace App\Http\ApiRequests;

use App\Helpers\ResponseData;
use Illuminate\Contracts\Validation\Validator;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\Exceptions\HttpResponseException;

abstract class CustomRequest extends FormRequest
{

    public function authorize(): bool
    {
        return true;
    }

    protected function failedValidation(Validator $validator): void
    {
        throw new HttpResponseException(
            ResponseData::error(
                'Data validation errors',
                [
                    'errors' => $validator->errors(),
                ],
                422
            )
        );
    }

    protected function failedAuthorization(): void
    {
        throw new HttpResponseException(
            ResponseData::error(
                'Unauthorized',
                [],
                403
            )
        );
    }
}