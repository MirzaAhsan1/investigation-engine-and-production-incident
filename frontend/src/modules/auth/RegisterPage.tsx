import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, User as UserIcon, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";
import { useRegisterMutation } from "../../api/authApi";
import useAuthStore from "../../store/authStore";
import { Button } from "../../components/ui/Button";

interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const [register, { isLoading, error, isSuccess }] = useRegisterMutation();
  const { isAuthenticated } = useAuthStore();

  const {
    register: rhfRegister,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch("password");

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard", { replace: true });
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await register({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      }).unwrap();
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1500);
    } catch {
      // error handled via RTK error state
    }
  };

  const apiError =
    error && "data" in error
      ? (error.data as any)?.detail || "Registration failed. Please try again."
      : null;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-50">Create your workspace</h2>
        <p className="text-sm text-slate-400 mt-1">
          Join the AI-powered incident command center.
        </p>
      </div>

      {apiError && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-sm text-rose-400">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{apiError}</span>
        </div>
      )}

      {isSuccess && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-2.5 text-sm text-emerald-400">
          <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>Account created successfully! Redirecting to login...</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-3">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
          <div className="relative">
            <UserIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Jane Smith"
              {...rhfRegister("full_name", { required: "Full name is required" })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.full_name ? "border-rose-500/50" : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.full_name && <p className="mt-1 text-xs text-rose-400">{errors.full_name.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Work Email</label>
          <div className="relative">
            <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="email"
              placeholder="sre@company.com"
              {...rhfRegister("email", {
                required: "Email is required",
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Invalid email" },
              })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.email ? "border-rose-500/50" : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.email && <p className="mt-1 text-xs text-rose-400">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="password"
              placeholder="Min. 8 characters"
              {...rhfRegister("password", {
                required: "Password is required",
                minLength: { value: 8, message: "At least 8 characters required" },
              })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.password ? "border-rose-500/50" : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.password && <p className="mt-1 text-xs text-rose-400">{errors.password.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Confirm Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="password"
              placeholder="Re-enter your password"
              {...rhfRegister("confirmPassword", {
                required: "Please confirm your password",
                validate: (val) => val === password || "Passwords do not match",
              })}
              className={`w-full pl-9 pr-4 py-2.5 text-sm bg-slate-950/80 border rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none transition-colors ${
                errors.confirmPassword ? "border-rose-500/50" : "border-slate-800 focus:border-indigo-500"
              }`}
            />
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-xs text-rose-400">{errors.confirmPassword.message}</p>
          )}
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full mt-2"
          isLoading={isLoading}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Create Account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-400">
        Already have an account?{" "}
        <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
          Sign in
        </Link>
      </p>
    </div>
  );
}
