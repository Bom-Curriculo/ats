<?php

namespace App\Http\Controllers\Api\User;

use App\Enums\UserGenderEnum;
use App\Enums\UserLanguageLevelEnum;
use App\Enums\UserQualificationTypeEnum;
use App\Helpers\ResponseData;
use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use App\Models\User;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;

class UserController extends Controller
{

    use UserProcessRelationsTrait, UserUploadsTrait;

    public function update(Request $request)
    {
        
        try{

            DB::transaction(function() use ($request){
                
                $request->merge($this->prepareForValidation($request));

                $request->validate([
                    'name' => ['string', 'min:2', 'max: 191'],
                    'password' => ['string', 'min:8'],
                    'resume_cv'       => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
                    'resume_linkedin' => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
                    'github_link'     => ['nullable', 'string'],
                    'site_link'       => ['nullable', 'string'],
                    'social_name' => ['nullable', 'string', 'min:2', 'max: 191'],
                    'phone' => ['nullable', 'string', 'min:11', 'max:15'],
                    'resume' => ['nullable', 'string'],
                    'resume_email' => ['nullable', 'email'],
                    'gender' => ['nullable', Rule::enum(UserGenderEnum::class)],
                    'is_pcd' => ['nullable', 'boolean'],
                    'path_certificate_pcd' => ['nullable', 'file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
                    'city' => ['nullable', 'string'],
                    'state' => ['nullable', 'string'],
                    'country' => ['nullable', 'string'],
                    'linkedin_link' => ['nullable', 'string'],                
                    
                    'skills'          => ['array'],
                    'skills.*.name'   => ['string', 'required'],
                    'skills.*.years'   => ['string', 'nullable'],

                    'experiences' => ['array'],
                    'experiences.*.company' => ['required', 'string'],
                    'experiences.*.role' => ['required', 'string'],
                    'experiences.*.start' => ['required', 'date'],
                    'experiences.*.end' => ['nullable', 'date'],
                    'experiences.*.description' => ['nullable', 'string'],
                    'experiences.*.is_actual' => ['required_unless:end,null', 'boolean'],
                    'experiences.*.city' => ['nullable', 'string'],
                    'experiences.*.state' => ['nullable', 'string'],
                    'experiences.*.country' => ['nullable', 'string'],

                    'qualifications' => ['array'],
                    'qualifications.*.type' => ['required', Rule::enum(UserQualificationTypeEnum::class)],
                    'qualifications.*.institution' => ['required', 'string'],
                    'qualifications.*.title' => ['required', 'string'],
                    'qualifications.*.start' => ['required', 'date'],
                    'qualifications.*.end' => ['nullable', 'date'],                
                    'qualifications.*.is_coursing' => ['required_unless:end,null', 'boolean'],


                    'languages' => [ 'array'],
                    'languages.*.level' => ['required', Rule::enum(UserLanguageLevelEnum::class)],
                    'languages.*.language' => ['required', 'string'],
                ]);

                $user = $request->user();

                $this->processSkillsUser($request->input('skills', []), $user);
                $this->processExperiencesUser($request->input('experiences', []), $user);
                $this->processQualificationsUser($request->input('qualifications', []), $user);
                $this->processLanguageUser($request->input('languages', []), $user);

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
                'user' => $request->user()->load(['skills', 'experiences', 'qualifications', 'languages']),
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

    protected function prepareForValidation(Request $request)
    {
        $experiences = $request->input('experiences', []);
        $qualifications = $request->input('qualifications', []);


        foreach ($experiences as $key => $value) {
            if (isset($value['is_actual'])) {
                $experiences[$key]['is_actual'] = filter_var($value['is_actual'], FILTER_VALIDATE_BOOLEAN);
            }
        }

        foreach ($qualifications as $key => $value) {
            if (isset($value['is_coursing'])) {
                $qualifications[$key]['is_coursing'] = filter_var($value['is_coursing'], FILTER_VALIDATE_BOOLEAN);
            }
        }

        return ([
            'experiences' => $experiences,
            'qualifications' => $qualifications,
            'is_pcd' => (bool) $request->is_pcd ?? false
        ]);
    }

}
