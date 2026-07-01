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
 * return ResponseData::success($data, $code, $message);
 * eg.: return ResponseData::success(['user_name' => 'John Doe'], 200, 'Request successful');
 * 
 * // For error response
 * return ResponseData::error($data, $code, $message);
 * eg.: return ResponseData::error(['error' => 'Invalid request'], 400, 'Bad request');
 * 
 * 
 * Error responses will be logged automatically if the code is 500 or higher.
 * eg.: return ResponseData::error(['error' => 'SMTP Error'], 500, 'Internal server error');
 * 
 * @author Gustavo Martim
 * 
 */

namespace App\Helpers;

use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Response;

final class ResponseData {

    protected static $defaultSuccessCode    = 200;
    protected static $defaultSuccessMessage = 'Request successful';

    protected static $defaultErrorCode      = 500;
    protected static $defaultErrorMessage   = 'Request failed, internal server error';

    protected static function handle(
        $data = [], 
        $code = null, 
        $message = null
    ) : JsonResponse|Response
    {
        $code = $code ?? self::$defaultSuccessCode;
        $message = $message ?? self::$defaultSuccessMessage;

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

    protected static function handleLog($message, $code, $data) : void
    {
        switch($code) {
            case $code >= 500:
                    self::handleErrorLog($message, $code, $data);
                break;

            default:
                    // do nothing
                break;

        }
        
    }

    protected static function handleErrorLog($message, $code, $data) : void
    {
        Log::error('[API][ERROR] - ' . $message, [
            'code'    => $code ?? self::$defaultErrorCode,
            'message' => $message ?? self::$defaultErrorMessage,
            'data'    => $data
        ]);
    }

    public static function success(
        $data, 
        $code, 
        $message
    ) : JsonResponse|Response 
    {
        return self::handle(
            $data, 
            $code ?? self::$defaultSuccessCode, 
            $message ?? self::$defaultSuccessMessage
        );
    }

    public static function error(
        $data, 
        $code, 
        $message
    ) : JsonResponse|Response 
    {

        self::handleLog($message, $code, $data);

        return self::handle(
            $data, 
            $code ?? self::$defaultErrorCode, 
            $message ?? self::$defaultErrorMessage
        );
    }

}