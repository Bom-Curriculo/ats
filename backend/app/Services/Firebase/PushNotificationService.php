<?php

namespace App\Services\Firebase;

use Exception;

class PushNotificationService {

    public function __construct(
        private array  $config = [],
        private null|string $token = null,
        private $meesage = null
    ){

        $this->config = config('services.firebase.mobile') ?? [];

        if(empty($this->config)) 
            throw new Exception('Service Firebase Mobile is not configured');

    }

}