import { Routes, Route } from "react-router-dom";

import Home from "../pages/home/Home";
import { Login } from "@/pages/auth/login";
import Register from "@/pages/auth/register";
import Dashboard from "@/pages/dashboard/Dashboard";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/protectRouter";
import MyResume from "@/pages/dashboard/my-resume/MyResume";
import ResumeUpload from "@/pages/resume-upload/ResumeUpload";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/resume-upload" element={<ResumeUpload />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/my-resume" element={<MyResume />} />
        </Route>
      </Route>
    </Routes>
  );
}
