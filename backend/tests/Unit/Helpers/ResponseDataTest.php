<?php

use App\Helpers\ResponseData;

it('returns correct response structure for success', function () {

    $response = ResponseData::success(
        'OK',
        ['name' => 'Gustavo'],
        200
    );

    $data = $response->getData(true);

    expect($data)
        ->toHaveKeys(['code', 'message', 'data']);

    expect($data['code'])->toBe(200);
});
