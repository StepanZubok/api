import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../api/axios";

export default function Home() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [postsLoading, setPostsLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState(new Date().toLocaleTimeString());
  const [searchTerm, setSearchTerm] = useState("");
  const [limit, setLimit] = useState(10);

  // Initial auth check
  useEffect(() => {
    let mounted = true;

    const fetchUser = async () => {
      try {
        await new Promise(r => setTimeout(r, 100));
        const res = await api.get("/me");
        
        if (mounted) {
          setUserData(res.data);
          console.log("Auth OK (initial)");
        }
      } catch (err) {
        console.error("Initial auth failed:", err.response?.data || err.message);
        if (mounted) {
          navigate("/login");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    
    fetchUser();

    return () => {
      mounted = false;
    };
  }, [navigate]);

  // Fetch posts - ONLY after auth is confirmed
  useEffect(() => {
    if (loading || !userData) {
      return;
    }

    let mounted = true;

    const fetchPosts = async () => {
      if (!mounted) return;

      try {
        setPostsLoading(true);
        console.log("Fetching posts...");
        
        // Add a small delay to ensure cookies are fully set
        await new Promise(r => setTimeout(r, 200));

        const params = new URLSearchParams();
        params.append('limit', limit);
        params.append('skip', 0);
        if (searchTerm) params.append('search', searchTerm);

        const url = `/posts?${params.toString()}`;
        console.log("Making request to:", url);

        const res = await api.get(url);
        
        if (mounted) {
          console.log("Posts response:", res.data);
          setPosts(res.data);
          console.log("Posts fetched:", res.data.length);
        }
      } catch (err) {
        console.error("Failed to fetch posts:", err);
        console.error("Error response:", err.response);
        console.error("Error details:", err.response?.data || err.message);
        
        if (mounted) {
          toast.error("Failed to load posts");
        }
      } finally {
        if (mounted) {
          setPostsLoading(false);
        }
      }
    };

    fetchPosts();

    return () => {
      mounted = false;
    };
  }, [loading, userData, searchTerm, limit]);

  // Periodic auth check
  useEffect(() => {
    if (!userData) return;

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
  }, [userData]);

  const handleLogout = async () => {
    try {
      await api.post("/logout");
      toast.success("Logged out");
      navigate("/login");
    } catch {
      toast.error("Logout failed");
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
  };

  if (loading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Home</h1>
          {userData && (
            <p className="text-gray-600">Welcome, {userData.email}</p>
          )}
          <p className="text-xs text-gray-400">Last auth check: {lastCheck}</p>
        </div>

        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search posts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-2">
          <label htmlFor="limit" className="text-sm text-gray-600">
            Posts per page:
          </label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="px-3 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Posts List */}
      {postsLoading ? (
        <div className="text-center p-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-500"></div>
          <p className="mt-2 text-gray-600">Loading posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center p-8 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No posts found</p>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="mt-2 text-blue-500 hover:underline"
            >
              Clear search
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((item) => (
            <div
              key={item.post.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex gap-4">
                {/* Vote Count */}
                <div className="flex flex-col items-center">
                  <div className="bg-blue-100 text-blue-700 font-bold rounded-full w-12 h-12 flex items-center justify-center">
                    {item.vote}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">votes</p>
                </div>

                {/* Post Content */}
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    {item.post.title}
                  </h2>
                  
                  {item.post.content && (
                    <p className="text-gray-600 mb-3">{item.post.content}</p>
                  )}

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>Post ID: {item.post.id}</span>
                    {item.post.created_at && (
                      <span>
                        {new Date(item.post.created_at).toLocaleDateString()}
                      </span>
                    )}
                    {item.post.published !== undefined && (
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          item.post.published
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {item.post.published ? "Published" : "Draft"}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Posts Count */}
      {!postsLoading && posts.length > 0 && (
        <div className="mt-6 text-center text-sm text-gray-600">
          Showing {posts.length} post{posts.length !== 1 ? "s" : ""}
        </div>
      )}
    </div>
  );
}