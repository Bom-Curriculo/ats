<?php

namespace App\Http\Controllers\Api\User;

use App\Enums\SystemUploadPrivatePathEnum;
use App\Helpers\ResponseData;
use App\Http\Controllers\Controller;
use App\Models\User;
use Exception;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\ValidationException;
use Services\ResumeFilesProccess;

class UserController extends Controller
{
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
                'skills.*'        => ['string']
            ]);
            
            $resumeCV = $request->file('resume_cv');
            $resumeLinkedin = $request->file('resume_linkedin');

            $pathResumeCv = null;
            $pathResumeLinkedin = null;
            $skills = $request->input('skills', []);

            if(!empty($resumeCV)){
                $pathResumeCv = 
                    $resumeCV
                        ->store(
                            SystemUploadPrivatePathEnum::PATH_UPLOAD_RESUME_CV
                            ->value
                        );

                if(!empty($user->resume_cv)){
                    Storage::delete($user->resume_cv);
                }

            }

            if(!empty($resumeLinkedin)){
                $pathResumeLinkedin = 
                    $resumeLinkedin
                        ->store(
                            SystemUploadPrivatePathEnum::PATH_UPLOAD_RESUME_LINKEDIN
                            ->value
                        );
                
                if(!empty($user->resume_linkedin)){
                    Storage::delete($user->resume_linkedin);
                }
            }
            
            $user->update([
                'resume_cv' => $pathResumeCv ?? $user->resumeCV,
                'resume_linkedin' => $pathResumeLinkedin ?? $user->resume_linkedin,
                'github_link' => $request->input('github_link', $user->github_link),
                'site_link' => $request->input('site_link', $user->site_link),
            ]);

            if(!empty($skills)){
                $mapSkills = array_map(function($skill){
                    return ['name' => $skill];
                }, $skills);
                $user->skills()->createMany((array) $mapSkills);
            }

            // Send proccess and handle it
            ResumeFilesProccess::handle();

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
            default => null,
        };

        if(!$typeFile || !Storage::exists($typeFile))
        {
            return ResponseData::error('Not Found', [
                'error' => 'The requested file has not found.'
            ], 404);
        }

        $fileUrl = Storage::temporaryUrl($typeFile, now()->addHour(2));

        return ResponseData::success('success', [
            'file_url' => $fileUrl
        ], 200);

    }

}
