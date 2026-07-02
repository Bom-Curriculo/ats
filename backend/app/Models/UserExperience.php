<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable([
    'user_id',
    'company',
    'role',
    'start',
    'end',
    'description',
    'is_actual',
    'city',
    'state',
    'country'
])]
class UserExperience extends Model
{
    public $cast = [
        'start' => 'date',
        'end'   => 'date',
        'is_actual' => 'boolean'
    ];

    public function user() : BelongsTo
    {
        return $this->belongsTo(User::class);
    }

}
