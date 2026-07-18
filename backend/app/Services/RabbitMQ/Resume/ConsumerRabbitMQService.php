<?php

namespace App\Services\RabbitMQ\Resume;

use Closure;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class ConsumerRabbitMQService
{
    protected AMQPStreamConnection $connection;

    public function __construct()
    {
        $config = config('queue.connections.rabbitmq_consumer');

        $this->connection = new AMQPStreamConnection(
            $config['hosts'][0]['host'],
            $config['hosts'][0]['port'],
            $config['hosts'][0]['user'],
            $config['hosts'][0]['password'],
            $config['hosts'][0]['vhost'] ?? '/'
        );
    }

    public function consume(string $queue, Closure $callback): void
    {
        $channel = $this->connection->channel();

        $channel->queue_declare(
            $queue,
            false,
            true,
            false,
            false
        );

        $channel->basic_qos(
            0,
            1,
            null
        );

        $channel->basic_consume(
            $queue,
            '',
            false,
            false,
            false,
            false,
            function (AMQPMessage $message) use ($callback) {

                try {

                    $payload = json_decode($message->body, true);

                    $callback($payload);

                    $message->ack();

                } catch (\Throwable $e) {

                    logger()->error($e);

                    $message->nack(false, false);
                }

            }
        );

        while ($channel->is_consuming()) {
            $channel->wait();
        }

        $channel->close();
        $this->connection->close();
    }
}
