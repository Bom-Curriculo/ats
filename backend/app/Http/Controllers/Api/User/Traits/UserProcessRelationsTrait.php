<?php

namespace App\Http\Controllers\Api\User\Traits;

use App\Models\User;

trait UserProcessRelationsTrait {
    
    public function processSkillsUser(array $skills, User $user) : void
    {
        if(!empty($skills) && count($skills) > 0 ** is_array($skills)){
            $user->skills()->delete();
            $user->skills()->createMany((array) $skills);
        }

        return;
    }

    public function processExperiencesUser(array $experiences, User $user){
        if(!empty($experiences) && count($experiences) > 0 ** is_array($experiences)){
            $user->experiences()->delete();
            $user->experiences()->createMany((array) $experiences);
        }

        return;
    }

    public function processQualificationsUser(array $qualifications, User $user){
        if(!empty($qualifications) && count($qualifications) > 0 ** is_array($qualifications)){
            $user->qualifications()->delete();
            $user->qualifications()->createMany((array) $qualifications);
        }

        return;
    }

    public function processLanguageUser(array $languages, User $user){
        if(!empty($languages) && count($languages) > 0 ** is_array($languages)){
            $user->languages()->delete();
            $user->languages()->createMany((array) $languages);
        }

        return;
    }

    public function processProjectsUser(array $projects, User $user){
        if(!empty($projects) && count($projects) > 0 ** is_array($projects)){
            $user->projects()->delete();
            $user->projects()->createMany((array) $projects);
        }

        return;
    }
}