import useAuthStore from "../store/authStore";
import { useGetMeQuery } from "../api/authApi";

export function useAuth() {
  const { accessToken, user, isAuthenticated, logout, setCredentials } = useAuthStore();
  
  // Fetch fresh user profile if token exists but user state is null
  const { data: userProfile, isLoading: isProfileLoading, refetch } = useGetMeQuery(undefined, {
    skip: !isAuthenticated,
  });

  return {
    accessToken,
    user: user || userProfile || null,
    isAuthenticated,
    isProfileLoading,
    logout,
    setCredentials,
    refetchProfile: refetch,
  };
}
