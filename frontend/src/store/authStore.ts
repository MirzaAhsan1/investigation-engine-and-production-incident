import { create } from "zustand";

export interface AuthState {
  accessToken: string | null;
  user: any;
  isAuthenticated: boolean;
  setCredentials: (credentials: { accessToken: string; user?: any }) => void;
  setUser: (user: any) => void;
  logout: () => void;
}

// On app initialization, read the token from localStorage
const storedToken = localStorage.getItem("accessToken");
const storedUser = JSON.parse(localStorage.getItem("user") || "null");

const useAuthStore = create<AuthState>((set) => ({
  accessToken: storedToken,
  user: storedUser,
  isAuthenticated: !!storedToken,

  setCredentials: ({ accessToken, user }) => {
    localStorage.setItem("accessToken", accessToken);
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    }
    set({
      accessToken,
      user: user || null,
      isAuthenticated: true,
    });
  },

  setUser: (user) => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
    set({ user });
  },

  logout: () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user");
    set({
      accessToken: null,
      user: null,
      isAuthenticated: false,
    });
  },
}));

export default useAuthStore;