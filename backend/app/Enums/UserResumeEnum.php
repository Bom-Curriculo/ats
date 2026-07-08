<?php

namespace App\Enums;

enum UserResumeEnum : string
{
    case PENDING = 'pending';
    case ANALYZE = 'analyze';
    case READY   = 'ready';
    case FAIL    = 'fail';
}
