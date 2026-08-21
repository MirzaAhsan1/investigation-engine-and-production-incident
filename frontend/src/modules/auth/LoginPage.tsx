import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, ArrowRight, AlertCircle } from "lucide-react";
import { useLoginMutation, useLazyGetMeQuery } from "../../api/authApi";
import useAuthStore from "../../store/authStore";
import { Button } from "../../components/ui/Button";

interface LoginFormData {
  email: string;
  password: string;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [login, { isLoading, error }] = useLoginMutation();
  const [getMe] = useLazyGetMeQuery();
  const { setCredentials, isAuthenticated } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard", { replace: true });
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      const result = await login(data).unwrap();
      setCredentials({ accessToken: result.access_token });
      try {
        const user = await getMe().unwrap();
        setCredentials({ accessToken: result.access_token, user });
      } catch {
        // Continue even if profile fetch fails
      }
      navigate("/dashboard", { replace: true });
    } catch {
      // error handled via RTK error state
    }
  };


  const apiError =
    error && "data" in error
      ? (error.data as any)?.detail || "Authentication failed. Please try again."
      : null;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-50">Sign in to your workspace</h2>
        <p className="text-sm text-slate-400 mt-1">
          Monitor, investigate, and resolve production incidents with AI.
        </p>
      </div>

      {apiError && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-sm text-rose-400">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{apiError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Work Email</label>
          <div className="relative">
            <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="email"
              autoComplete="email"
              placeholder="sre@yourcompany.com"
              {...register("email", {
                required: "Email is required",
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Invalid email address" },
              })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.email
                  ? "border-rose-500/50 focus:border-rose-500"
                  : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.email && (
            <p className="mt-1 text-xs text-rose-400">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="password"
              autoComplete="current-password"
              placeholder="••••••••••••"
              {...register("password", {
                required: "Password is required",
                minLength: { value: 8, message: "Password must be at least 8 characters" },
              })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.password
                  ? "border-rose-500/50 focus:border-rose-500"
                  : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.password && (
            <p className="mt-1 text-xs text-rose-400">{errors.password.message}</p>
          )}
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full mt-2"
          isLoading={isLoading}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Sign In
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-400">
        Don&apos;t have an account?{" "}
        <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
          Create workspace
        </Link>
      </p>
    </div>
  );
}
