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
   
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'level' => UserLanguageLevelEnum::class
        ];
    }

    public function user() : BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
