<?php

namespace App\Actions;

use App\Models\User;
use App\Services\Firebase\PushNotificationService;
use Exception;
use Illuminate\Http\JsonResponse;
use Kreait\Firebase\Exception\FirebaseException;
use Kreait\Firebase\Exception\MessagingException;

class SendPushNotificationAction
{
    public static function send(User $user, $title, $body): JsonResponse
    {
        try {

            $service = new PushNotificationService;

            foreach ($user->devices as $device) {

                $service->sendToToken(
                    token: $device->fcm_token,
                    payload: [
                        'title' => $title,
                        'body' => $body,
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
