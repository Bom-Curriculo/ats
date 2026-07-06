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
        Schema::create('resume_analytics', function (Blueprint $table) {
            $table->id();

            $table->uuid('analysis_request_id')->nullable();
            $table->unsignedBigInteger('user_id')->index();
            $table->string('status');
            $table->json('error')->nullable();

            $table->json('header')->nullable();
            $table->json('experiences')->nullable();
            $table->json('projects')->nullable();
            $table->json('qualifications')->nullable();
            $table->json('skills')->nullable();
            $table->json('languages')->nullable();
            $table->json('others')->nullable();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('resume_data');
    }
};
