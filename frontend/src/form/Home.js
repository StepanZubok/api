import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../api/axios";

export default function Home() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastCheck, setLastCheck] = useState(
    new Date().toLocaleTimeString()
  );

  // Initial auth check
  useEffect(() => {
    const fetchUser = async () => {
      try {
        // Small delay to allow cookies to settle after login
        await new Promise(r => setTimeout(r, 100));

        const res = await api.get("/me");
        setUserData(res.data);
        console.log("Auth OK (initial)");
      } catch (err) {
        console.error("Initial auth failed:", err.response?.data || err.message);
        // Axios interceptor handles redirect if refresh fails
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // Periodic auth check (keeps refresh token flow alive)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        await api.get("/me");
        setLastCheck(new Date().toLocaleTimeString());
        console.log("Auth OK (periodic)");
      } catch (err) {
        console.error("Periodic auth failed:", err.response?.data || err.message);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleLogout = async () => {
    try {
      await api.post("/logout");
      toast.success("Logged out");
      navigate("/login");
    } catch {
      toast.error("Logout failed");
    }
  };

  if (loading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Home</h1>
          {userData && (
            <p className="text-gray-600">
              Welcome, {userData.email}
            </p>
          )}
          <p className="text-xs text-gray-400">
            Last auth check: {lastCheck}
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
