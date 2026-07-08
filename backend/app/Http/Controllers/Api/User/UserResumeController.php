<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;

class UserResumeController extends Controller
{
    public function __invoke(Request $request)
    {
        try{   

            $resumes =  UserResume::where('user_id', $request->user()->id)
                            ->orderByDesc('created_at')
                            ->get();

            return ResponseData::success('Success', [
                'data' => $resumes
            ]);

        }catch(Exception $exception)
        {
             return ResponseData::error('Server error', [
                'error' => $exception->getMessage()
            ],
            500);
        }
    }
}
