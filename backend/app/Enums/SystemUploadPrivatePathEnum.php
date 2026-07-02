<?php

namespace App\Enums;

enum SystemUploadPrivatePathEnum : string
{
    case PATH_UPLOAD_RESUME_CV = 'uploads/resumes/cvs';
    case PATH_UPLOAD_RESUME_LINKEDIN = 'uploads/resumes/linkedins';
}
