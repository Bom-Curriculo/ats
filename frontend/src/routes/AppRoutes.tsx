import { Routes, Route } from "react-router-dom";

import Home from "../pages/home/Home";
import { Login } from "@/pages/auth/login";
import Register from "@/pages/auth/register";
import Dashboard from "@/pages/dashboard/Dashboard";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import MyCurriculum from "@/pages/dashboard/my-curriculum/MyCurriculum";
import JobAnalysis from "@/pages/dashboard/job-analysis/JobAnalysis";
import Settings from "@/pages/dashboard/settings/Settings";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/Dashboard" element={<Dashboard />} />
        <Route path="/Dashboard" element={<JobAnalysis />} />
        <Route path="/Dashboard" element={<Settings />} />
        <Route path="/Dashboard" element={<MyCurriculum />} />
      </Route>
    </Routes>
  );
}
