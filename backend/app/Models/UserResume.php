<?php

namespace App\Models;

use App\Enums\UserResumeEnum;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;

#[Fillable([
    'user_id',
    'original_file_path_cv',
    'original_file_path_linkedin',
    'processed_file_path',
    'status',
    'processed_at',
    'observation'
])]
class UserResume extends Model
{
    use HasUuids;

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
            'status' => UserResumeEnum::class
        ];
    }

    public function user() : BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function analytic() : HasOne
    {
        return $this->hasOne(UserResumeAnalytic::class, 'user_resume_id', 'id');
    }
}
