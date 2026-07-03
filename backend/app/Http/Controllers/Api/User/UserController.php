<?php

namespace App\Http\Controllers\Api\User;

use App\Enums\UserGenderEnum;
use App\Enums\UserLanguageLevelEnum;
use App\Enums\UserQualificationTypeEnum;
use App\Helpers\ResponseData;
use App\Http\Controllers\Api\User\Traits\UserProccessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use App\Models\User;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\Rule;
use Illuminate\Validation\ValidationException;
use App\Services\ResumeFilesProccess;

class UserController extends Controller
{

    use UserProccessRelationsTrait, UserUploadsTrait;

    public function storeValidateResume(Request $request)
    {

        DB::beginTransaction();
        try{

            $user = User::find($request->user()->id);

            $request->validate([
                'resume_cv'       => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
                'resume_linkedin' => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
                'github_link'     => ['nullable', 'string'],
                'site_link'       => ['nullable', 'string'],
                'skills'          => ['nullable', 'array'],
                'skills.*.name'   => ['required', 'string']
            ]);
            
            $resumeCV = $request->file('resume_cv');
            $resumeLinkedin = $request->file('resume_linkedin');

            $pathResumeCv = null;
            $pathResumeLinkedin = null;
            $skills = $request->input('skills', []);

            if(!empty($resumeCV)){
                $pathResumeCv = $this->storeCvResume($request, $user);
            }

            if(!empty($resumeLinkedin)){
                $pathResumeLinkedin = $this->storeLinkedinResume($request, $user);
            }
            
            $user->update([
                'resume_cv' => $pathResumeCv ?? $user->resumeCV,
                'resume_linkedin' => $pathResumeLinkedin ?? $user->resume_linkedin,
                'github_link' => $request->input('github_link', $user->github_link),
                'site_link' => $request->input('site_link', $user->site_link),
            ]);

            $this->proccessSkillsUser($skills, $user);

            DB::commit();
            return ResponseData::success('User Updated', ['message' => 'User and upload has been updated.'], 200);

        }catch(ValidationException $exception){
            DB::rollback();
            return ResponseData::error('Validation error', ['errors' => $exception->errors()], 422);
        }catch(Exception $exception){
            DB::rollback();
            return ResponseData::error('Server Error', ['errors' => $exception->getMessage()], 500);
        }
    }

    public function getResumesFiles(Request $request, string $type = 'cv')
    {
        $user = $request->user();
        
        $typeFile = match ($type) {
            'cv' => $user->resume_cv,
            'linkedin' => $user->resume_linkedin,
            'pcd' => $user->path_certificate_pcd,
            default => null,
        };

        if(!$typeFile || !Storage::exists($typeFile))
        {
            return ResponseData::error('Not Found', [
                'error' => 'The requested file has not found.'
            ], 404);
        }

        $fileUrl = Storage::temporaryUrl($typeFile, now()->addDay());

        return ResponseData::success('success', [
            'file_url' => $fileUrl
        ], 200);

    }

    public function update(Request $request)
    {
        DB::beginTransaction();
        try{
            
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

            $user = User::where('id', $request->user()->id)
                        ->with([
                            'skills',
                            'experiences',
                            'qualifications',
                            'languages'
                        ])
                        ->first();

            $this->proccessSkillsUser($request->input('skills', []), $user);
            $this->proccessExperiencesUser($request->input('experiences', []), $user);
            $this->proccessQualificationsUser($request->input('qualifications', []), $user);
            $this->proccessLanguageUser($request->input('languages', []), $user);

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

            DB::commit();
            return ResponseData::success('Success', [
                'user' => $user->load(['skills', 'experiences', 'qualifications', 'languages']),
            ]);

        }catch(ValidationException $validator){

            DB::rollBack();
            return ResponseData::error('Validation failed.', [
                'errors' => $validator->errors()
            ],
            422);

        }catch(Exception $exception){

            DB::rollBack();
            return ResponseData::error('Server error', [
                'error' => $exception->getMessage()
            ],
            500);

        }
    }

    public function proccessResumes(Request $request)
    {
        try{
            $user = User::find($request->user()->id);
            ResumeFilesProccess::handle($user);
            
            return ResponseData::success('Success', [
                'message' => 'Files are sended to proccess worker'
            ], 200);

        }catch(Exception $exception){
            return ResponseData::error('Failed',
            [
                'message' => $exception->getMessage()
            ], 500);
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
