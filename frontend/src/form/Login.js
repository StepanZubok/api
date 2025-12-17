import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../api/axios";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState([]);
  const navigate = useNavigate();

  const addDebugLog = (message, type = "info") => {
    const timestamp = new Date().toLocaleTimeString();
    const log = { message, type, timestamp };
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
    setDebugInfo(prev => [...prev, log]);
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  setDebugInfo([]);

  addDebugLog("🚀 Login process started", "info");
  addDebugLog(`📧 Email: ${email}`, "info");

  const startTime = Date.now();

  try {
    addDebugLog("📝 Creating form data...", "info");
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    addDebugLog("📤 Sending POST request to /login", "info");

    const response = await api.post("/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const duration = Date.now() - startTime;
    
    addDebugLog(`✅ Login successful (${duration}ms)`, "success");
    addDebugLog("🍪 Cookies set by server", "success");
    
    if (response.data?.access_token) {
      const tokenPreview = response.data.access_token.substring(0, 20) + "...";
      addDebugLog(`🔑 Access token preview: ${tokenPreview}`, "info");
    }

    toast.success("Login successful");
    
    addDebugLog("🔄 Redirecting to /home...", "info");
    
    // ✅ Add small delay to ensure cookies are set
    await new Promise(resolve => setTimeout(resolve, 100));
    
    navigate("/home");

  } catch (err) {
    const duration = Date.now() - startTime;
    addDebugLog(`❌ Login failed (${duration}ms)`, "error");
    addDebugLog(`Error: ${err.response?.data?.detail || err.message}`, "error");
    toast.error(err.response?.data?.detail || "Invalid credentials");
  } finally {
    setLoading(false);
  }
};

  const getLogColor = (type) => {
    switch(type) {
      case "success": return "text-green-600";
      case "error": return "text-red-600";
      case "warning": return "text-yellow-600";
      default: return "text-gray-700";
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

      {/* Debug Console */}
      {debugInfo.length > 0 && (
        <div className="mt-6 border rounded-lg p-4 bg-gray-50 max-h-64 overflow-y-auto">
          <h3 className="font-semibold mb-2 text-sm">🔍 Debug Console</h3>
          <div className="space-y-1 font-mono text-xs">
            {debugInfo.map((log, index) => (
              <div key={index} className={getLogColor(log.type)}>
                <span className="text-gray-400">[{log.timestamp}]</span> {log.message}
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-center mt-4 text-sm">
        Don't have an account? <Link to="/register" className="text-yellow-400 hover:underline">Sign up</Link>
      </p>
    </div>
  );
}