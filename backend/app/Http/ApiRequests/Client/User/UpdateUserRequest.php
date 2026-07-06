<?php

namespace App\Http\ApiRequests\Client\User;

use App\Enums\UserGenderEnum;
use App\Enums\UserLanguageLevelEnum;
use App\Enums\UserQualificationTypeEnum;
use App\Http\ApiRequests\CustomRequest;
use Illuminate\Validation\Rule;

class UpdateUserRequest extends CustomRequest
{

    public function rules(): array
    {
        return [
            'name' => ['string', 'min:3', 'max: 128'],
            'password' => ['string', 'min:8', 'max:64'],
            'resume_cv'       => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
            'resume_linkedin' => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
            'github_link'     => ['nullable', 'string', 'min:9', 'max:255'],
            'site_link'       => ['nullable', 'string', 'min:9', 'max:255'],
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

            'projects' => [ 'array'],
            'projects.*.title' => ['required', 'string', 'max:181', 'min:3'],
            'projects.*.date' => ['required', 'string', 'max:4', 'min:4'],
            'projects.*.technologies' => ['required', 'string'],
            'projects.*.description' => ['required', 'string'],
            'projects.*.url' => ['required', 'string', 'max: 255', 'min: 7'],
        ];
    }

    protected function prepareForValidation(): void
    {
        $experiences = $this->input('experiences', []);
        $qualifications = $this->input('qualifications', []);


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

        $this->merge ([
            'experiences' => $experiences,
            'qualifications' => $qualifications,
            'is_pcd' => (bool) $this->input('is_pcd', false)
        ]);
    }

}