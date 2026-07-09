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
        Schema::table('resume_analytics', function (Blueprint $table) {
            $table->uuid('user_resume_id')->nullable()->after('analysis_request_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('resume_analytics', function (Blueprint $table) {
            $table->dropColumn('user_resume_id');
        });
    }
};
