<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use App\Enums\UserGenderEnum;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

#[Fillable([
    'name', 
    'email', 
    'password', 
    'resume_cv', 
    'resume_linkedin', 
    'github_link', 
    'site_link',
    'social_name',
    'phone',
    'resume',
    'resume_email',
    'gender',
    'is_pcd',
    'path_certificate_pcd',
    'city',
    'state',
    'country',
    'linkedin_link',
    'last_resume_id'
])]
#[Hidden(['password', 'remember_token', 'resume_cv', 'resume_linkedin', 'path_certificate_pcd', 'last_resume_id'])]
class User extends Authenticatable
{
    /** @use HasFactory<UserFactory> */
    use HasFactory, Notifiable, HasApiTokens;

    protected $fillable = [
        'fcm_token',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'gender' => UserGenderEnum::class
        ];
    }

    public function skills() : HasMany
    {
        return $this->hasMany(UserSkill::class);
    }

    public function experiences() : HasMany
    {
        return $this->hasMany(UserExperience::class);
    }

    public function qualifications() : HasMany
    {
        return $this->hasMany(UserQualification::class);
    }

    public function languages() : HasMany
    {
        return $this->hasMany(UserLanguage::class);
    }

    public function projects() : HasMany
    {
        return $this->hasMany(UserProject::class);
    }

    public function resumes() : HasMany
    {
        return $this->hasMany(UserResume::class);
    }

    public function resumeAnalytics() : HasMany
    {
        return $this->hasMany(UserResumeAnalytic::class);
    }

    public function devices(): HasMany
    {
        return $this->hasMany(UserDevice::class);
    }

}
