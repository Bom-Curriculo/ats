<?php

namespace App\Models;

use App\Enums\UserLanguageLevelEnum;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable([
    'language',
    'level'
])]
class UserLanguage extends Model
{
    public $casts = [
        'level' => UserLanguageLevelEnum::class
    ];

    public function user() : BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
