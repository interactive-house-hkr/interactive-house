"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Home, Eye, EyeOff } from "lucide-react";
import { auth } from "@/lib/auth";

const BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1";

const USE_MOCK_AUTH = false;

export default function LoginPage() {
  const router = useRouter();

  const [isSignUp, setIsSignUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  useEffect(() => {
  if (auth.isLoggedIn()) {
    router.replace("/dashboard");
  }
}, []);

  const submitLabel = useMemo(() => {
    if (loading) return "Please wait...";
    return isSignUp ? "Sign Up" : "Sign In";
  }, [loading, isSignUp]);

  const toggleMode = () => {
    setIsSignUp((prev) => !prev);
    setError("");
    setShowPassword(false);
    setForm({
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    });
  };

  const validateForm = () => {
    if (form.username.trim().length < 3) {
      return "Username must be at least 3 characters";
    }

    if (form.password.length < 6) {
      return "Password must be at least 6 characters";
    }

    if (isSignUp && !form.email.trim()) {
      return "Email is required";
    }

    if (isSignUp && form.password !== form.confirmPassword) {
      return "Passwords do not match";
    }

    return "";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      if (USE_MOCK_AUTH) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        localStorage.setItem("token", "mock-token-12345");
        localStorage.setItem("username", form.username);
        router.push("/dashboard");
        return;
      }

      const endpoint = isSignUp ? "/auth/register" : "/auth/login";

      const body = isSignUp
        ? {
            username: form.username.trim(),
            email: form.email.trim(),
            password: form.password,
          }
        : {
            username: form.username.trim(),
            password: form.password,
          };

      const response = await fetch(`${BASE_URL}${endpoint}`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  body: JSON.stringify(body),
});

// IMPORTANT: read raw first (prevents silent parsing issues)
const text = await response.text();
console.log("RAW RESPONSE:", text);

// parse manually so we SEE failures clearly
const data = JSON.parse(text);
console.log("PARSED DATA:", data);

if (!response.ok || data.status === "error") {
  throw new Error(
    data?.detail?.[0]?.msg ||
      data?.message ||
      data?.detail ||
      "Authentication failed"
  );
}

// store session
auth.setSession({
  access_token: data.access_token,
  refresh_token: data.refresh_token,
  user_id: data.user_id,
  username: form.username.trim(),
});

// verify storage immediately
console.log("TOKEN STORED:", localStorage.getItem("token"));
console.log("REFRESH STORED:", localStorage.getItem("refreshToken"));

router.push("/dashboard");

    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-100">
            <Home className="h-7 w-7 text-teal-600" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">Interactive House</h1>
          <p className="text-sm text-gray-500">Smart Home Control</p>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg shadow-gray-200/50">
          <h2 className="mb-1 text-lg font-semibold text-gray-900">
            {isSignUp ? "Create Account" : "Welcome Back"}
          </h2>
          <p className="mb-6 text-sm text-gray-500">
            {isSignUp ? "Sign up to get started" : "Sign in to your account"}
          </p>

          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                type="text"
                value={form.username}
                onChange={(e) =>
                  setForm({ ...form, username: e.target.value })
                }
                className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-gray-900 placeholder-gray-400 transition-shadow focus:border-transparent focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Enter username"
                required
              />
            </div>

            {isSignUp && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">
                  Email
                </label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-gray-900 placeholder-gray-400 transition-shadow focus:border-transparent focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Enter email"
                  required
                />
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={form.password}
                  onChange={(e) =>
                    setForm({ ...form, password: e.target.value })
                  }
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 pr-11 text-gray-900 placeholder-gray-400 transition-shadow focus:border-transparent focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {isSignUp && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={form.confirmPassword}
                  onChange={(e) =>
                    setForm({ ...form, confirmPassword: e.target.value })
                  }
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-gray-900 placeholder-gray-400 transition-shadow focus:border-transparent focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Confirm password"
                  required
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-teal-500 py-2.5 font-medium text-white transition-colors hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitLabel}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={toggleMode}
              className="text-sm font-medium text-teal-600 hover:text-teal-700"
            >
              {isSignUp
                ? "Already have an account? Sign In"
                : "Need an account? Sign Up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}