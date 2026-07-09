<?php

namespace App\Http\ApiRequests\Client\Resume;

use App\Http\ApiRequests\CustomRequest;

class NewResumeRequest extends CustomRequest
{

    public function rules(): array
    {
        return [
            'resume_cv'       => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
            'resume_linkedin' => ['file', 'mimes:pdf,doc,docx', 'min:5', 'max:10240'],
            'github_link'     => ['nullable', 'string', 'min:9', 'max:255'],
            'site_link'       => ['nullable', 'string', 'min:9', 'max:255'],
            'skills'          => ['nullable', 'array'],
            'skills.*.name'   => ['required', 'string']
        ];
    }

}