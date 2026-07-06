<?php

namespace App\Console\Commands;

use App\Services\RabbitMQ\Resume\ConsumerRabbitMQService;
use App\Services\RabbitMQ\Resume\Response\ProcessResumeResponse;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

#[Signature('app:rabbit-consume')]
#[Description('Consumer RabbitMQ Resumes Worker')]
class ConsumeRabbitMQ extends Command
{
    
    public function handle(ConsumerRabbitMQService $consumer)
    {
        $queue = config('queue.connections.rabbitmq_consumer.queue');

        $this->info("Consumindo {$queue}");

        $consumer->consume($queue, function (array $payload) {

            Log::info('Requisição de entrada encontrada na fila:', [$payload]);
            ProcessResumeResponse::handle($payload);

        });
    }
}
