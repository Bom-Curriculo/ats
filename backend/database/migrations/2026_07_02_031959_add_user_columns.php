<?php

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
        Schema::table('users', function (Blueprint $table) {
            $table->string('resume_cv')->nullable()->after('email');
            $table->string('resume_linkedin')->nullable()->after('resume_cv');
            $table->string('github_link')->nullable()->after('resume_linkedin');
            $table->string('site_link')->nullable()->after('github_link');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn(['resume_cv', 'resume_linkedin', 'github_link', 'site_link']);
        });
    }
};
