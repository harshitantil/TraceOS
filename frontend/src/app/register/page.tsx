"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", organization_name: "" });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { access_token } = await api.register(form);
      setToken(access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-trace-900 to-trace-700">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-slate-900 mb-1">Create Account</h1>
        <p className="text-slate-500 text-sm mb-6">Start your TraceOS workspace</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { key: "name", label: "Your Name" },
            { key: "email", label: "Email", type: "email" },
            { key: "password", label: "Password", type: "password" },
            { key: "organization_name", label: "Organization Name" },
          ].map(({ key, label, type }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
              <input
                type={type || "text"}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                className="w-full border border-slate-200 rounded-lg px-3 py-2"
                required
              />
            </div>
          ))}
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" className="w-full bg-trace-600 text-white py-2 rounded-lg hover:bg-trace-700">
            Create Account
          </button>
        </form>
        <p className="text-sm text-slate-500 mt-4 text-center">
          Have an account? <Link href="/login" className="text-trace-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
