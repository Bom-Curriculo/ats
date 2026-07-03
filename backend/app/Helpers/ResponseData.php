<?php

/** 
 * Handle response data for API requests, 
 * including success and error responses, 
 * with logging for errors.
 * 
 * 
 * How to use:
 * 
 * use App\Helpers\ResponseData;
 * 
 * // For success response
 * return ResponseData::success(string $message, array|object $data, int $code);
 * eg.: return ResponseData::success('Request successful', ['user_name' => 'John Doe'], 200);
 * 
 * // For error response
 * return ResponseData::error(string $message, array|object $data, int $code);
 * eg.: return ResponseData::error('Bad request', ['error' => 'Invalid request'], 400);
 * 
 * 
 * Error responses will be logged automatically if the code is 500 or higher.
 * eg.: return ResponseData::error('Internal server error', ['error' => 'SMTP Error'], 500);
 * 
 * @author Gustavo Martim
 * 
 */

namespace App\Helpers;

use Illuminate\Http\JsonResponse;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Response;

final class ResponseData {

    protected const defaultSuccessCode    = 200;
    protected const defaultSuccessMessage = 'Request successful';

    protected const defaultErrorCode      = 500;
    protected const defaultErrorMessage   = 'Request failed, internal server error';

    protected static function handle(
        string $message = null,
        array|Collection|LengthAwarePaginator $data = [], 
        int $code = null
    ) : JsonResponse|Response
    {
        $code = $code ?? self::defaultSuccessCode;
        $message = $message ?? self::defaultSuccessMessage;

        if(self::isCollection($data)) {
            $data = $data->toArray();
        }

        if(self::isPaginator($data)) {
            $data = [
                'current_page' => $data->currentPage(),
                'per_page'     => $data->perPage(),
                'total'        => $data->total(),
                'last_page'    => $data->lastPage(),
                'data'         => $data->items()
            ];
        }

        return Response::json([
            'code'    => $code,
            'message' => $message,
            'data'    => $data
        ], $code);
    }

    protected static function isCollection($data) : bool
    {
        return $data instanceof \Illuminate\Support\Collection;
    }

    protected static function isPaginator($data) : bool
    {
        return $data instanceof \Illuminate\Pagination\LengthAwarePaginator;
    }

    protected static function handleLog($message, $data, $code) : void
    {
        if ($code >= 500) {
            self::handleErrorLog($message, $data, $code);
        }
    }

    protected static function handleErrorLog($message, $data, $code) : void
    {
        Log::error('[API][ERROR] - ' . $message, [
            'code'    => $code ?? self::defaultErrorCode,
            'message' => $message ?? self::defaultErrorMessage,
            'data'    => $data
        ]);
    }

    public static function success(
        string $message = self::defaultSuccessMessage,
        array|Collection|LengthAwarePaginator $data = [], 
        int $code = self::defaultSuccessCode
    ) : JsonResponse|Response 
    {
        return self::handle(
            $message,
            $data,             
            $code
        );
    }

    public static function error(
        string $message = self::defaultErrorMessage,
        array|Collection|LengthAwarePaginator $data = [], 
        int $code = self::defaultErrorCode
    ) : JsonResponse|Response 
    {

        self::handleLog($message, $data, $code);

        return self::handle(
            $message,
            $data,
            $code
        );
    }

}