import { Routes, Route } from "react-router-dom";

import Home from "../pages/home/Home";
import { Login } from "@/pages/auth/login";
import Register from "@/pages/auth/register";
import { ForgotPassword } from "@/pages/auth/forgot-password";
import Dashboard from "@/pages/dashboard/Dashboard";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { ProtectedRoute } from "@/components/protectRouter";
import MyResume from "@/pages/dashboard/my-resume/MyResume";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/my-resume" element={<MyResume />} />
        </Route>
      </Route>
    </Routes>
  );
}
