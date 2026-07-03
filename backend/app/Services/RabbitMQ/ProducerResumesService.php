<?php

namespace App\Services\RabbitMQ;

use App\Helpers\ResponseData;
use App\Jobs\ResumeProcessingPublisher;
use App\Models\User;
use Exception;
use Illuminate\Http\Request;

class ProducerResumesService {

    public function __invoke(Request $request)
    {
        try{
            
            $user = User::find($request->user()->id);
            ResumeProcessingPublisher::dispatch($user)->onConnection('rabbitmq_producer');
            
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