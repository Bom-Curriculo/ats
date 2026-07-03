<?php

namespace App\Console\Commands;

use App\Services\ConsumerRabbitMQService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

#[Signature('app:rabbit-consume')]
#[Description('Command description')]
class ConsumeRabbitMQ extends Command
{

    public function handle(ConsumerRabbitMQService $consumer)
    {
        $queue = 'resumes_bot_queue';

        $this->info("Consumindo {$queue}");

        $consumer->consume($queue, function (array $payload) {

            Log::info('Requisição encontrada na fila:', [$payload])
            // Seu processamento aqui

            /*
            app(ResumeProcessor::class)
                ->process($payload);
            */

        });
    }
}
