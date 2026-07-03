<?php 

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

it('stores cv resume file', function () {

    Storage::fake('local');

    $user = authUser();

    $request = new \Illuminate\Http\Request();
    $request->files->set('resume_cv', UploadedFile::fake()->create('cv.pdf'));

    $service = new class {
        use \App\Http\Controllers\Api\User\Traits\UserUploadsTrait;
    };

    $path = $service->storeCvResume($request, $user);

    expect($path)->not->toBeNull();
});