<?php

namespace App\Http\Controllers\Api\User;

use App\Helpers\ResponseData;
use App\Http\ApiRequests\Client\User\UpdateUserRequest;
use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use Exception;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class UserController extends Controller
{

    use UserProcessRelationsTrait, UserUploadsTrait;

    public function update(UpdateUserRequest $request)
    {
        
        try{

            DB::transaction(function() use ($request){
                
                $user = $request->user();

                $this->processSkillsUser($request->input('skills', []), $user);
                $this->processExperiencesUser($request->input('experiences', []), $user);
                $this->processQualificationsUser($request->input('qualifications', []), $user);
                $this->processLanguageUser($request->input('languages', []), $user);
                $this->processProjectsUser($request->input('projects', []), $user);

                $pathResumeCv = $user->resume_cv;
                $pathResumeLinkedin = $user->resume_linkedin;
                $pathCertificatePCD = $user->path_certificate_pcd;

                if(!empty($request->file('resume_cv'))){
                    $pathResumeCv = $this->storeCvResume($request, $user);
                }

                if(!empty($request->file('resume_linkedin'))){
                    $pathResumeLinkedin = $this->storeLinkedinResume($request, $user);
                }

                if(!empty($request->file('path_certificate_pcd'))){
                    $pathCertificatePCD = $this->storePcdCertificate($request, $user);
                }

                // Remove Files from request
                $request = $request->except([
                    'resume_cv',
                    'resume_linkedin',
                    'path_certificate_pcd',
                    'skills',
                    'experiences',
                    'qualifications',
                    'languages'
                ]);

                // Override Files path to request
                $data = array_merge([
                    'resume_cv' => $pathResumeCv,
                    'resume_linkedin' => $pathResumeLinkedin,
                    'path_certificate_pcd' => $pathCertificatePCD
                ], $request);
                

                $user->update($data);
            });
            
            return ResponseData::success('Success', [
                'user' => $request->user()->load(['skills', 'experiences', 'qualifications', 'languages', 'projects']),
            ]);

        }catch(ValidationException $validator){

            return ResponseData::error('Validation failed.', [
                'errors' => $validator->errors()
            ],
            422);

        }catch(Exception $exception){

            return ResponseData::error('Server error', [
                'error' => $exception->getMessage()
            ],
            500);

        }
    }

}
