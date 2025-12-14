import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import axios from "axios";

export default function Home() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await axios.post("http://192.168.1.250:8000/logout", {}, {
        withCredentials: true,
      });
      toast.success("Logged out successfully");
      navigate("/login");
    } catch (error) {
      toast.error("Logout failed");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto pt-10 p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold mb-4">Welcome Home! 🏠</h1>
          <p className="text-lg text-gray-700 mb-6">
            You are successfully logged in!
          </p>
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-6 rounded-lg"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}