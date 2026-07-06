<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable([
    'analysis_request_id',
    'user_id',
    'status',
    'error',
    'header',
    'experiences',
    'projects',
    'qualifications',
    'skills',
    'languages',
    'others',
])]
class ResumeAnalytic extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'error'          => 'array',
            'header'         => 'array',
            'experiences'    => 'array',
            'projects'       => 'array',
            'qualifications' => 'array',
            'skills'         => 'array',
            'languages'      => 'array',
            'others'         => 'array',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
