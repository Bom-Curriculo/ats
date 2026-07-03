<?php

namespace App\Http\Controllers\Api\User\Traits;

use App\Enums\SystemUploadPrivatePathEnum;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

trait UserUploadsTrait {
    
    protected function storeCvResume(Request $request, User $user){
        $file = $request->file('resume_cv');
        $path = $file->store(
                    SystemUploadPrivatePathEnum::PATH_UPLOAD_RESUME_CV->value
                );

        if(!empty($user->resume_cv)){
            Storage::delete($user->resume_cv);
        }

        return $path;
    }
    protected function storeLinkedinResume(Request $request, User $user){
        $path = $request->file('resume_linkedin')->store(
                    SystemUploadPrivatePathEnum::PATH_UPLOAD_RESUME_LINKEDIN->value
                );

        if(!empty($user->resume_linkedin)){
            Storage::delete($user->resume_linkedin);
        }

        return $path;
    }
    protected function storePcdCertificate(Request $request, User $user){
        $path = $request->file('path_certificate_pcd')->store(
                    SystemUploadPrivatePathEnum::PATH_UPLOAD_CERTIFICATE_PCD
                    ->value
                );

        if(!empty($user->path_certificate_pcd)){
            Storage::delete($user->path_certificate_pcd);
        }

        return $path;
    }
}