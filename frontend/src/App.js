import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./form/Login";
import Register from "./form/Register";
import ForgotPassword from "./form/ForgotPassword";

function App() {
  return (
    <div className="min-h-screen bg-yellow-400 flex justify-center items-center">
      <div className="py-12 px-12 bg-white rounded-2xl shadow-xl z-20 w-full max-w-md">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
