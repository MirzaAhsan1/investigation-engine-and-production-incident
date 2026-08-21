import { useUIStore } from "../store/uiStore";

export function useToast() {
  const { toasts, addToast, removeToast } = useUIStore();

  const toast = {
    success: (title: string, message: string) =>
      addToast({ type: "success", title, message }),
    error: (title: string, message: string) =>
      addToast({ type: "error", title, message }),
    warning: (title: string, message: string) =>
      addToast({ type: "warning", title, message }),
    info: (title: string, message: string) =>
      addToast({ type: "info", title, message }),
  };

  return { toasts, toast, removeToast };
}
