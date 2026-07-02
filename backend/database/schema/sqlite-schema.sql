CREATE TABLE "migrations"(
  "id" integer primary key autoincrement not null,
  "migration" varchar not null,
  "batch" integer not null
);
CREATE TABLE "users"(
  "id" integer primary key autoincrement not null,
  "name" varchar not null,
  "email" varchar not null,
  "email_verified_at" datetime,
  "password" varchar not null,
  "remember_token" varchar,
  "resume_cv" varchar,
  "resume_linkedin" varchar,
  "github_link" varchar,
  "site_link" varchar,
  "social_name" varchar,
  "phone" varchar,
  "resume" text,
  "resume_email" varchar,
  "gender" varchar check("gender" in('male', 'female', 'another')),
  "is_pcd" tinyint(1) not null default '0',
  "path_certificate_pcd" varchar,
  "city" varchar,
  "state" varchar,
  "country" varchar,
  "linkedin_link" varchar,
  "created_at" datetime,
  "updated_at" datetime
);
CREATE UNIQUE INDEX "users_email_unique" on "users"("email");
CREATE TABLE "password_reset_tokens"(
  "email" varchar not null,
  "token" varchar not null,
  "created_at" datetime,
  primary key("email")
);
CREATE TABLE "sessions"(
  "id" varchar not null,
  "user_id" integer,
  "ip_address" varchar,
  "user_agent" text,
  "payload" text not null,
  "last_activity" integer not null,
  primary key("id")
);
CREATE INDEX "sessions_user_id_index" on "sessions"("user_id");
CREATE INDEX "sessions_last_activity_index" on "sessions"("last_activity");
CREATE TABLE "cache"(
  "key" varchar not null,
  "value" text not null,
  "expiration" integer not null,
  primary key("key")
);
CREATE INDEX "cache_expiration_index" on "cache"("expiration");
CREATE TABLE "cache_locks"(
  "key" varchar not null,
  "owner" varchar not null,
  "expiration" integer not null,
  primary key("key")
);
CREATE INDEX "cache_locks_expiration_index" on "cache_locks"("expiration");
CREATE TABLE "jobs"(
  "id" integer primary key autoincrement not null,
  "queue" varchar not null,
  "payload" text not null,
  "attempts" integer not null,
  "reserved_at" integer,
  "available_at" integer not null,
  "created_at" integer not null
);
CREATE INDEX "jobs_queue_index" on "jobs"("queue");
CREATE TABLE "job_batches"(
  "id" varchar not null,
  "name" varchar not null,
  "total_jobs" integer not null,
  "pending_jobs" integer not null,
  "failed_jobs" integer not null,
  "failed_job_ids" text not null,
  "options" text,
  "cancelled_at" integer,
  "created_at" integer not null,
  "finished_at" integer,
  primary key("id")
);
CREATE TABLE "failed_jobs"(
  "id" integer primary key autoincrement not null,
  "uuid" varchar not null,
  "connection" varchar not null,
  "queue" varchar not null,
  "payload" text not null,
  "exception" text not null,
  "failed_at" datetime not null default CURRENT_TIMESTAMP
);
CREATE INDEX "failed_jobs_connection_queue_failed_at_index" on "failed_jobs"(
  "connection",
  "queue",
  "failed_at"
);
CREATE UNIQUE INDEX "failed_jobs_uuid_unique" on "failed_jobs"("uuid");
CREATE TABLE "personal_access_tokens"(
  "id" integer primary key autoincrement not null,
  "tokenable_type" varchar not null,
  "tokenable_id" integer not null,
  "name" text not null,
  "token" varchar not null,
  "abilities" text,
  "last_used_at" datetime,
  "expires_at" datetime,
  "created_at" datetime,
  "updated_at" datetime
);
CREATE INDEX "personal_access_tokens_tokenable_type_tokenable_id_index" on "personal_access_tokens"(
  "tokenable_type",
  "tokenable_id"
);
CREATE UNIQUE INDEX "personal_access_tokens_token_unique" on "personal_access_tokens"(
  "token"
);
CREATE INDEX "personal_access_tokens_expires_at_index" on "personal_access_tokens"(
  "expires_at"
);
CREATE TABLE "password_reset_otps"(
  "id" integer primary key autoincrement not null,
  "user_id" integer not null,
  "otp" varchar not null,
  "expires_at" datetime not null,
  "used_at" datetime,
  "created_at" datetime,
  "updated_at" datetime
);
CREATE TABLE "user_skills"(
  "id" integer primary key autoincrement not null,
  "user_id" integer not null,
  "name" varchar not null,
  "years" integer,
  "created_at" datetime,
  "updated_at" datetime,
  foreign key("user_id") references "users"("id") on delete cascade
);
CREATE TABLE "user_experiences"(
  "id" integer primary key autoincrement not null,
  "user_id" integer not null,
  "company" varchar not null,
  "role" varchar not null,
  "start" date not null,
  "end" date,
  "description" text,
  "is_actual" tinyint(1) not null default '0',
  "city" varchar,
  "state" varchar,
  "country" varchar,
  "created_at" datetime,
  "updated_at" datetime,
  foreign key("user_id") references "users"("id") on delete cascade
);
CREATE TABLE "user_qualifications"(
  "id" integer primary key autoincrement not null,
  "user_id" integer not null,
  "type" varchar check("type" in('elementary_education', 'high_school', 'extracurricular_course', 'technical_course', 'undergraduate_degree', 'postgraduate_degree', 'master_degree', 'doctorate_degree')) not null,
  "institution" varchar not null,
  "title" varchar not null,
  "start" date not null,
  "end" date,
  "is_coursing" tinyint(1) not null default '0',
  "created_at" datetime,
  "updated_at" datetime,
  foreign key("user_id") references "users"("id") on delete cascade
);
CREATE TABLE "user_languages"(
  "id" integer primary key autoincrement not null,
  "user_id" integer not null,
  "language" varchar not null,
  "level" varchar check("level" in('beginner', 'intermediate', 'advanced', 'fluent', 'native')) not null,
  "created_at" datetime,
  "updated_at" datetime,
  foreign key("user_id") references "users"("id") on delete cascade
);

INSERT INTO migrations VALUES(1,'0001_01_01_000000_create_users_table',1);
INSERT INTO migrations VALUES(2,'0001_01_01_000001_create_cache_table',1);
INSERT INTO migrations VALUES(3,'0001_01_01_000002_create_jobs_table',1);
INSERT INTO migrations VALUES(4,'2026_07_01_000429_create_personal_access_tokens_table',1);
INSERT INTO migrations VALUES(5,'2026_07_02_012824_password_reset_otps',1);
INSERT INTO migrations VALUES(6,'2026_07_02_031959_add_user_columns',1);
INSERT INTO migrations VALUES(7,'2026_07_02_032229_create_user_skills_table',1);
INSERT INTO migrations VALUES(8,'2026_07_02_165024_schema_tables',1);
