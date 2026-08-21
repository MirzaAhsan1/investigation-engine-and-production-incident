import { create } from "zustand";

export interface ToastMessage {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
}

export interface UIState {
  sidebarOpen: boolean;
  searchQuery: string;
  selectedIncidentId: string | null;
  activeFilterSeverity: string;
  activeFilterStatus: string;
  toasts: ToastMessage[];
  
  toggleSidebar: () => void;
  setSearchQuery: (query: string) => void;
  setSelectedIncidentId: (id: string | null) => void;
  setSeverityFilter: (severity: string) => void;
  setStatusFilter: (status: string) => void;
  addToast: (toast: Omit<ToastMessage, "id">) => void;
  removeToast: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  searchQuery: "",
  selectedIncidentId: null,
  activeFilterSeverity: "all",
  activeFilterStatus: "all",
  toasts: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSelectedIncidentId: (selectedIncidentId) => set({ selectedIncidentId }),
  setSeverityFilter: (activeFilterSeverity) => set({ activeFilterSeverity }),
  setStatusFilter: (activeFilterStatus) => set({ activeFilterStatus }),
  
  addToast: (toast) =>
    set((state) => {
      const id = Math.random().toString(36).substring(2, 9);
      return { toasts: [...state.toasts, { ...toast, id }] };
    }),

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
