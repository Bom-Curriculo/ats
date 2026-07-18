<?php

use App\Enums\UserGenderEnum;
use App\Enums\UserLanguageLevelEnum;
use App\Enums\UserQualificationTypeEnum;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {

        Schema::create('user_experiences', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')
                ->constrained('users')
                ->onDelete('cascade');

            $table->string('company');
            $table->string('role');
            $table->date('start');
            $table->date('end')->nullable();
            $table->text('description')->nullable();
            $table->boolean('is_actual')->default(false);
            $table->string('city')->nullable();
            $table->string('state')->nullable();
            $table->string('country')->nullable();

            $table->timestamps();
        });

        Schema::create('user_qualifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')
                ->constrained('users')
                ->onDelete('cascade');

            $table->enum('type', [
                UserQualificationTypeEnum::ELEMENTARY->value,
                UserQualificationTypeEnum::HIGHSCHOOL->value,
                UserQualificationTypeEnum::EXTRACOURSE->value,
                UserQualificationTypeEnum::TECHNICAL_COURSE->value,
                UserQualificationTypeEnum::GRADUATE_DEGREE->value,
                UserQualificationTypeEnum::POSTGRADUATE_DEGREE->value,
                UserQualificationTypeEnum::MASTER_DEGREE->value,
                UserQualificationTypeEnum::DOCTORATE_DEGREE->value,
            ]);

            $table->string('institution');
            $table->string('title');
            $table->date('start');
            $table->date('end')->nullable();
            $table->boolean('is_coursing')->default(false);

            $table->timestamps();
        });

        Schema::create('user_languages', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')
                ->constrained('users')
                ->onDelete('cascade');

            $table->string('language');
            $table->enum('level', [
                UserLanguageLevelEnum::BEGINNER->value,
                UserLanguageLevelEnum::INTERMEDIATE->value,
                UserLanguageLevelEnum::ADVANCED->value,
                UserLanguageLevelEnum::FLUENT->value,
                UserLanguageLevelEnum::NATIVE->value,
            ]);

            $table->timestamps();
        });

        Schema::table('users', function (Blueprint $table) {
            $table->string('social_name')->nullable()->after('name');
            $table->string('phone')->nullable()->after('social_name');
            $table->text('resume')->nullable()->after('phone');
            $table->string('resume_email')->nullable()->after('email');
            $table->enum('gender', [
                UserGenderEnum::MALE->value,
                UserGenderEnum::FEMALE->value,
                UserGenderEnum::ANOTHER->value,
            ])->nullable()->after('name');
            $table->boolean('is_pcd')->default(false)->after('gender');
            $table->string('path_certificate_pcd')->nullable()->after('is_pcd');
            $table->string('city')->nullable()->after('site_link');
            $table->string('state')->nullable()->after('city');
            $table->string('country')->nullable()->after('state');
            $table->string('linkedin_link')->nullable()->after('github_link');
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('user_experiences');
        Schema::dropIfExists('user_qualifications');
        Schema::dropIfExists('user_languages');
        Schema::dropColumns('users', [
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
        ]);
    }
};
