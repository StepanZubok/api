import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import axios from "axios";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      await axios.post("http://192.168.1.250:8000/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        withCredentials: true,
      });

      toast.success("Login successful");
      navigate("/home");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-center mb-6">Sign in</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yellow-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yellow-400"
          />
        </div>
        <div className="text-right">
          <Link to="/forgot-password" className="text-sm text-yellow-400 hover:underline">
            Forgot password?
          </Link>
        </div>
        <button
          type="submit"
          disabled={loading}
          className={`w-full ${loading ? "bg-yellow-200" : "bg-yellow-400 hover:bg-yellow-500"} text-black font-semibold py-2 rounded-lg`}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p className="text-center mt-4 text-sm">
        Don't have an account? <Link to="/register" className="text-yellow-400 hover:underline">Sign up</Link>
      </p>
    </div>
  );
}