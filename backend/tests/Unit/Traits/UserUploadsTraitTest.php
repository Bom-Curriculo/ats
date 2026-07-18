<?php

use App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

it('stores cv resume file', function () {

    Storage::fake('local');

    $user = authUser();

    $request = new Request;
    $request->files->set('resume_cv', UploadedFile::fake()->create('cv.pdf'));

    $service = new class
    {
        use UserUploadsTrait;
    };

    $path = $service->storeCvResume($request, $user);

    expect($path)->not->toBeNull();
});
