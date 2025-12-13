import { useState } from "react";
import { Link } from "react-router-dom";
import React from "react";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Reset password link sent to:", email);
    alert(`If an account exists for ${email}, a reset link has been sent.`);
  };

  return (
    <React.Fragment>
      <div>
        <h1 className="text-2xl font-bold text-center mb-6">Forgot Password</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 rounded-lg transition"
          >
            Send Reset Link
          </button>
        </form>

        <p className="text-center mt-4 text-sm">
          Remembered your password?{" "}
          <Link to="/login" className="text-yellow-400 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </React.Fragment>
  );
}
