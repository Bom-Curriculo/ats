<?php

namespace App\Actions;

use Exception;
use Illuminate\Http\Request;
use App\Services\Firebase\PushNotificationService;
use Kreait\Firebase\Exception\FirebaseException;
use Kreait\Firebase\Exception\MessagingException;
use App\Models\User;

class SendPushNotificationAction
{
    public static function send(User $user, $title, $body): \Illuminate\Http\JsonResponse
    {
        try {

            $service = new PushNotificationService();

            foreach ($user->devices as $device) {

                $service->sendToToken(
                    token: $device->fcm_token,
                    payload: [
                        'title' => $title,
                        'body' => $body
                    ]
                );

            }
            return response()->json([
                'success' => true,
            ]);

        } catch (Exception $exception) {

            return response()->json([
                'success' => false,
                'message' => $exception->getMessage(),
            ], 500);

        } catch (MessagingException|FirebaseException $e) {
            return response()->json([
                'success' => false,
                'message' => $e->getMessage(),

            ], 505);
        }
    }
}