<?php

namespace App\Services\RabbitMQ\Resume;

use App\Helpers\ResponseData;
use App\Jobs\Api\RabbitMQ\Resumes\ResumeProcessingPublisher;
use Exception;
use Illuminate\Http\Request;

class ProducerResumesService {

    public function __invoke(Request $request)
    {
        try{

            ResumeProcessingPublisher::dispatch($request->user())->onConnection('rabbitmq_producer');
            
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