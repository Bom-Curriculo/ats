<?php

use Illuminate\Http\UploadedFile;

it('can validate resume upload', function () {

    $auth = actingAsUser();

    $file = UploadedFile::fake()
        ->create('resume.pdf', 100, 'application/pdf');

    $response = $this
        ->withHeaders($auth['headers'])
        ->postJson('/api/client/resumes/validate-resume', [
            'resume_cv' => $file,
            'github_link' => 'https://github.com/test',
        ]);

    $response->assertOk();
});
