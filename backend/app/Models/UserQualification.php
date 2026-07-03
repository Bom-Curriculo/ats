<?php

namespace App\Models;

use App\Enums\UserQualificationTypeEnum;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable([
    'user_id',
    'type',
    'institution',
    'title',
    'start',
    'end',
    'is_coursing'
])]
class UserQualification extends Model
{

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'start'       => 'date',
            'end'         => 'date',
            'is_coursing' => 'boolean',
            'type'        => UserQualificationTypeEnum::class
        ];
    }

    public function user() : BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
