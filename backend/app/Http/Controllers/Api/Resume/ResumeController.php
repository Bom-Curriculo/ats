<?php

namespace App\Http\Controllers\Api\Resume;

use App\Helpers\ResponseData;
use App\Http\ApiRequests\Client\Resume\NewResumeRequest;
use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;
use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use App\Http\Controllers\Controller;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\ValidationException;

class ResumeController extends Controller
{

    use UserProcessRelationsTrait, UserUploadsTrait;

    public function storeNewResume(NewResumeRequest $request)
    {

        try{

            DB::transaction(function() use ($request){
                $user = $request->user();
                
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

                if(!empty($pathResumeCv) || !empty($pathResumeLinkedin)){
                    $user->resumes()->create([
                        'original_file_path_cv' => $pathResumeCv,
                        'original_file_path_linkedin' => $pathResumeLinkedin
                    ]);
                }
                $this->processSkillsUser($skills, $user);

            });
            
            return ResponseData::success('User Updated', ['message' => 'User and upload has been updated.'], 200);

        }catch(ValidationException $exception){
            return ResponseData::error('Validation error', ['errors' => $exception->errors()], 422);
        }catch(Exception $exception){
            return ResponseData::error('Server Error', ['errors' => $exception->getMessage()], 500);
        } catch (\Throwable $exception) {
            return ResponseData::error('Server Error', ['errors' => $exception->getMessage()], 500);
        }
    }

    public function getResumesFiles(Request $request)
    {
        $user = $request->user();
        $type = $request->input('type', 'cv');

        $typeFile = match ($type) {
            'cv' => $user->resume_cv,
            'linkedin' => $user->resume_linkedin,
            'pcd' => $user->path_certificate_pcd,
            default => $user->resume_cv,
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

}
