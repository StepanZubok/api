import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../api/axios";

export default function Home() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastCheck, setLastCheck] = useState(new Date().toLocaleTimeString());

  // Initial fetch
  useEffect(() => {
    const fetchUserData = async () => {
      // Add delay to ensure cookies are processed
      await new Promise(resolve => setTimeout(resolve, 100));
      
      try {
        console.log('🔍 Initial fetch - Fetching user data...');
        console.log('🍪 Document cookies:', document.cookie);
        
        const response = await api.get("/me");
        setUserData(response.data);
        console.log('✅ User data loaded:', response.data);
      } catch (err) {
        console.error('❌ Initial fetch failed:', err);
        console.error('Error details:', err.response?.data);
        console.error('Error status:', err.response?.status);
        
        // Don't redirect immediately - let's see what's happening
        // Uncomment this after debugging:
        // navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData(); 
  }, []);

  // Periodic check to test token refresh (every 30 seconds)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        console.log('🔄 Periodic check - verifying authentication...');
        const response = await api.get("/me");
        setLastCheck(new Date().toLocaleTimeString());
        console.log('✅ Auth check passed at', lastCheck);
      } catch (err) {
        console.error('❌ Auth check failed:', err);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [lastCheck]);

  const handleLogout = async () => {
    try {
      await api.post("/logout");
      toast.success("Logged out successfully");
      navigate("/login");
    } catch (err) {
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
          {userData ? (
            <p className="text-gray-600">Welcome, {userData.email}!</p>
          ) : (
            <p className="text-red-600">⚠️ Not authenticated - check console</p>
          )}
          <p className="text-xs text-gray-400 mt-1">
            Last auth check: {lastCheck}
          </p>
          <p className="text-xs text-yellow-600">
            Access token: 2min | Refresh token: 14.4min
          </p>
          <p className="text-xs text-gray-500 mt-2">
            🍪 Cookies: {document.cookie || '(none)'}
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
