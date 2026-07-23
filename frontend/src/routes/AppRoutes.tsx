import { Routes, Route } from "react-router-dom";

import Home from "../pages/home/Home";
import { Login } from "@/pages/auth/login";
import Register from "@/pages/auth/register";
import { ForgotPassword } from "@/pages/auth/forgot-password";
import Dashboard from "@/pages/dashboard/Dashboard";
import MyCurriculum from "@/pages/dashboard/my-curriculum/MyCurriculum";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/protectRouter";
import MyResume from "@/pages/dashboard/my-resume/MyResume";
import Editor from "@/pages/dashboard/editor/Editor";
import JobAnalysis from "@/pages/dashboard/job-analysis/JobAnalysis";
import JobDetails from "@/pages/dashboard/job-analysis/JobDetails";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/editor" element={<Editor />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/my-resume" element={<MyResume />} />
          <Route path="/my-curriculum" element={<MyCurriculum />} />
          <Route path="/job-analysis" element={<JobAnalysis />} />
          <Route path="/job-analysis/:id" element={<JobDetails />} />
        </Route>
      </Route>
    </Routes>
  );
}
