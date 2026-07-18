<?php

use App\Http\Controllers\Api\User\Traits\UserProcessRelationsTrait;

it('syncs user skills correctly', function () {

    $user = authUser();

    $service = new class
    {
        use UserProcessRelationsTrait;
    };

    $service->processSkillsUser([
        ['name' => 'PHP', 'years' => 5],
        ['name' => 'Laravel', 'years' => 3],
    ], $user);

    expect($user->skills()->count())->toBe(2);
});

it('replaces old skills when syncing', function () {

    $user = authUser();

    $user->skills()->create([
        'name' => 'Old Skill',
        'years' => 1,
    ]);

    $service = new class
    {
        use UserProcessRelationsTrait;
    };

    $service->processSkillsUser([
        ['name' => 'New Skill', 'years' => 5],
    ], $user);

    expect($user->skills()->count())->toBe(1);
    expect($user->skills()->first()->name)->toBe('New Skill');
});
