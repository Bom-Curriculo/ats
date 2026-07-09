<?php

use App\Enums\UserResumeEnum;
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
        Schema::create('user_resumes', function (Blueprint $table) {
            $table->uuid('id');
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
            $table->string('original_file_path_cv')->nullable();
            $table->string('original_file_path_linkedin')->nullable();
            $table->string('processed_file_path')->nullable();
            $table->enum('status', [
                UserResumeEnum::PENDING->value,
                UserResumeEnum::ANALYZE->value,
                UserResumeEnum::READY->value,
                UserResumeEnum::FAIL->value
            ])->default(
                UserResumeEnum::PENDING->value,
            );
            $table->timestamp('processed_at')->nullable();
            $table->text('observation')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('user_resumes');
    }
};
