<?php

namespace App\OpenApi\Schemas;

use OpenApi\Attributes as OA;

#[OA\Schema(
    schema: 'ApiSuccessResponse',
    properties: [
        new OA\Property(property: 'code', type: 'integer', example: 200),
        new OA\Property(property: 'message', type: 'string', example: 'Request successful'),
        new OA\Property(property: 'data', type: 'object'),
    ]
)]
class ApiSuccessResponse
{
    //
}
