<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Models\UserResumeAnalytic;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;

class UserResumeController extends Controller
{
    public function index(Request $request)
    {
        try{   

            $resumes =  UserResume::query()->where('user_id', $request->user()->id)
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

    public function showResumeAnalytic(Request $request, int $resume){

        $analytic = UserResume::query()->find($resume)->analytic;

        if(!$analytic || $analytic->user_id !== $request->user()->id){
            return ResponseData::error(
                'Not found',
                [
                    'error' => 'Resume not found'
                ],
                404
            );
        }

        return ResponseData::success(
            'Success',
            $analytic->toArray(),
            200
        );
    }
}
