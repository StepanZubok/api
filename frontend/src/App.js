import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Login from "./form/Login";
import Register from "./form/Register";
import ForgotPassword from "./form/ForgotPassword";
import Home from "./form/Home";

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<PageWrapper><Login /></PageWrapper>} />
        <Route path="/register" element={<PageWrapper><Register /></PageWrapper>} />
        <Route path="/forgot-password" element={<PageWrapper><ForgotPassword /></PageWrapper>} />
        <Route path="/home" element={<Home />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
}

function PageWrapper({ children }) {
  return (
    <div className="min-h-screen bg-yellow-400 flex justify-center items-center">
      <div className="py-12 px-12 bg-white rounded-2xl shadow-xl z-20 w-full max-w-md">
        {children}
      </div>
    </div>
  );
}

export default App;