<?php

namespace App\Jobs\Api\RabbitMQ\Resumes;

use App\Actions\SendPushNotificationAction;
use App\Enums\UserResumeEnum;
use App\Models\UserResumeAnalytic;
use App\Models\User;
use App\Models\UserResume;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;
use Throwable;

class ResumeProcessingConsumer implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public array $resume
    )
    {
        //
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        UserResumeAnalytic::query()->create($this->resume['resume'] ?? $this->resume);
        if($this->resume['resume_id'] || $this->resume->resume_id ){
            $resume = UserResume::find($this->resume['resume_id'] ?? $this->resume->resume_id);
            if($resume){
                $resume->update([
                    'status' => UserResumeEnum::ANALYZE
                ]);
            }
        }

        $user = User::query()->find($this->resume['user_id']);
        if($user){

            /**
             * For success
             */
            //            $service->sendToToken(
            //                token: 'cy4bSjq-RLuLaWiMDsY7i2:APA91bH6DHwLmkb_66yx7loOVsaWFuM2C9KHseXOspixhd0RTAhkxFTLj2NBDKqL7bI5EMrlW92S6e4T8ekruDVq_aWxvzmIVHfWUA1cJOrxnDNTaAKMrog',
            //                payload: [
            //                    'title' => '🚀 Falta só mais um passo!',
            //                    'body'  => 'Escolha as informações para montar seu currículo.'
            //                ]
            //            );

            /**
             * For errors
             */
            //            $service->sendToToken(
            //                token: 'cy4bSjq-RLuLaWiMDsY7i2:APA91bH6DHwLmkb_66yx7loOVsaWFuM2C9KHseXOspixhd0RTAhkxFTLj2NBDKqL7bI5EMrlW92S6e4T8ekruDVq_aWxvzmIVHfWUA1cJOrxnDNTaAKMrog',
            //                payload: [
            //                    'title' => '⚠️ Algo deu errado',
            //                    'body'  => 'Ocorreu um erro ao preparar seu currículo. Tente novamente.'
            //                ]
            //            );

            SendPushNotificationAction::send(
                user: $user,
                title: '🚀 Falta só mais um passo!',
                body: 'Escolha as informações para montar seu currículo.'
            );
        }
    }

    public function failed(Throwable $exception): void
    {
        Log::channel('rabbit_resumes')->error('Job ResumeProcessingConsumer failed definitively', [
            'exception' => $exception->getMessage(),
            'payload' => $this->resume,
            'trace' => $exception->getTraceAsString()
        ]);
    }
}
