<?php

it('can get resume file url', function () {

    $auth = actingAsUser();

    $response = $this
        ->withHeaders($auth['headers'])
        ->getJson('/api/client/resumes/files?type=cv');

    $response->assertNotFound();
});
