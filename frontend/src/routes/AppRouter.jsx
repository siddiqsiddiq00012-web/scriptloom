import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "../pages/Landing/LandingPage";
import Login from "../pages/Auth/Login";
import Register from "../pages/Auth/Register";
import Dashboard from "../pages/App/Dashboard";
import ProjectDetail from "../pages/App/ProjectDetail";
import BillingPage from "../pages/Billing/BillingPage";
import SettingsPage from "../pages/Settings/SettingsPage";
import ContentLibrary from "../pages/ContentLibrary/ContentLibrary";
import ProtectedRoute from "../components/common/ProtectedRoute";
import ResourceWorkspace from "../components/workspace/ResourceWorkspace";

import "./AppRouter.css";

function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />

        <Route path="/billing" element={
          <ProtectedRoute>
            <BillingPage />
          </ProtectedRoute>
        } />

        <Route path="/billing/success" element={
          <ProtectedRoute>
            <BillingPage />
          </ProtectedRoute>
        } />

        <Route path="/billing/cancel" element={
          <ProtectedRoute>
            <BillingPage />
          </ProtectedRoute>
        } />

        <Route path="/settings" element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        } />

        <Route path="/content" element={
          <ProtectedRoute>
            <ContentLibrary />
          </ProtectedRoute>
        } />
        
        <Route path="/projects/:projectId" element={
          <ProtectedRoute>
            <ProjectDetail />
          </ProtectedRoute>
        } />
        
        <Route path="/projects/:projectId/media/:mediaId" element={
          <ProtectedRoute>
            <ResourceWorkspace />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRouter;