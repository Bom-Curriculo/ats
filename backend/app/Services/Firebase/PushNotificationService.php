<?php

namespace App\Services\Firebase;

use Exception;
use Kreait\Firebase\Exception\FirebaseException;
use Kreait\Firebase\Exception\MessagingException;
use Kreait\Firebase\Factory;
use Kreait\Firebase\Messaging;
use Kreait\Firebase\Messaging\CloudMessage;
use Kreait\Firebase\Messaging\Notification;
use Kreait\Firebase\Messaging\AndroidConfig;
use Kreait\Firebase\Messaging\ApnsConfig;

class PushNotificationService
{
    private array $config = [];

    private Messaging $messaging;

    /**
     * @throws Exception
     */
    public function __construct()
    {
        $this->config = config('services.firebase.mobile') ?? [];

        if (empty($this->config)) {
            throw new Exception('Service Firebase Mobile is not configured');
        }

        $factory = (new Factory())->withServiceAccount([
            'type' => 'service_account',
            'project_id' => $this->config['credential']['projectId'],
            'client_email' => $this->config['credential']['clientEmail'],
            'private_key' => $this->normalizePrivateKey(
                $this->config['credential']['privateKey']
            ),
        ]);

        $this->messaging = $factory->createMessaging();
    }

    /**
     * Envia uma notificação para um token específico.
     *
     * @throws MessagingException
     * @throws FirebaseException
     */
    public function sendToToken(string $token, array $payload): array
    {
        $message = CloudMessage::new()
            ->withToken($token)
            ->withNotification(
                Notification::create(
                    $payload['title'],
                    $payload['body']
                )
            )
            ->withData([
                'route' => $payload['route'] ?? '/',
                'click_action' => 'FLUTTER_NOTIFICATION_CLICK',
                ...($payload['data'] ?? []),
            ])
            ->withAndroidConfig(
                AndroidConfig::fromArray([
                    'priority' => 'high',
                    'notification' => [
                        'channel_id' => 'flower_foreground_channel',
                        'icon' => 'ic_stat_flower',
                    ],
                ])
            )
            ->withApnsConfig(
                ApnsConfig::fromArray([
                    'headers' => [
                        'apns-push-type' => 'alert',
                        'apns-priority' => '10',
                    ],
                    'payload' => [
                        'aps' => [
                            'sound' => 'default',
                            'badge' => 1,
                        ],
                    ],
                ])
            );

        return $this->messaging->send($message);
    }

    /**
     * Normaliza a chave privada armazenada no .env.
     */
    private function normalizePrivateKey(string $privateKey): string
    {
        return str_replace(
            ["\r\n", '\r\n', '\n'],
            "\n",
            trim($privateKey)
        );
    }
}