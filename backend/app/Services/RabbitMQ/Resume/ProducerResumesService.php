<?php

namespace App\Services\RabbitMQ\Resume;

use App\Helpers\ResponseData;
use App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher;
use App\Models\UserResume;
use Exception;
use Illuminate\Http\Request;

class ProducerResumesService {

    public function __invoke(Request $request)
    {
        try{
            
            if(!$request->filled('user_resume_id'))
            {
                $resume = UserResume::find($request->input('user_resume_id'));
                if($resume && $request->user()->id !== $resume->user_id){
                    return ResponseData::success('Not found!', [
                        'message' => 'Resume not found for this user.'
                    ], 404);
                }
            }

            ResumeProcessingPublisher::dispatch($request->user(), $request->user_resume_id ?? null)->onConnection('rabbitmq_producer');
            
            return ResponseData::success('Success', [
                'message' => 'Processed to worker successfuly'
            ], 200);

        }catch(Exception $exception){
            return ResponseData::error('Failed',
            [
                'message' => $exception->getMessage()
            ], 500);
        }
       
    }

}