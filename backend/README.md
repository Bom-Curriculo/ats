# ATS Resume Builder 🚀

ATS Resume Builder is an open-source backend system built with **Laravel 13** that generates and manages professional resumes optimized for Applicant Tracking Systems (ATS).

The system supports authentication, resume management, file uploads, structured user profiles, and asynchronous processing using RabbitMQ.

---

## 📌 Repository

👉 GitHub: https://github.com/Bom-Curriculo/ats

---

## 📬 API Documentation (Postman)

👉 Postman Collection: https://documenter.getpostman.com/view/10306778/2sBY4HSibu#6f5a8d4d-17fc-480f-acb6-427998c905e5

The Postman collection includes all API endpoints:

- Authentication flows
- User profile management
- Resume upload & validation
- File retrieval (secure storage access)
- RabbitMQ processing endpoints

---

## ⚙️ Tech Stack

- PHP 8.4+
- Laravel 13
- Laravel Sanctum (API Authentication)
- MySQL / PostgreSQL
- RabbitMQ (asynchronous processing)
- PHPUnit + Pest (testing)
- Local / S3-compatible storage

---

## 📌 Requirements

Before running the project, ensure your environment has:

- PHP 8.4+
- Composer 2+
- MySQL 8+ or PostgreSQL 14+
- Node.js (optional)
- RabbitMQ server (required, for async processing)
- Docker (recommended)

---

## 🧠 Compatibility Notes

This project uses modern PHP and Laravel features:

- PHP 8.4 typed properties
- Enums for domain modeling
- Strict typing
- Laravel 13 architecture patterns
- Service-based business logic
- Queue-driven async processing

---

## 🚀 Features

### 🔐 Authentication
- User registration
- Login with Sanctum token
- OTP password recovery
- Secure logout

---


### ⚡ Async Processing (RabbitMQ)
- Resume processing queue
- Job-based architecture
- Decoupled service layer
- Future-ready for microservices integration

---

## 📦 Installation

### 1. Clone repository

```bash
git clone https://github.com/Bom-Curriculo/ats.git
cd ats
```

### 2. Clone repository

```bash
composer install
```
### 3. Environment setup

```bash
cp .env.example .env
php artisan key:generate
```

#### 3.1. SETUP .ENV

```bash
configure .env file
```

### 4. Run Migrations And Seeds

```bash
php artisan migrate --seed
```

### 5. Start the server

```bash
php artisan serve
```

### 6. Run RabbitMQ Consumer

```bash
php artisan app:rabbit-consume
```