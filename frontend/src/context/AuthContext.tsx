import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { customersApi, userApi } from "../lib/api";
import { decodeJwt, isTokenExpired } from "../lib/jwt";

interface Profile {
  token: string;
  customerId: string;
  userId: string;
  email: string;
  name?: string;
}

interface AuthContextValue {
  profile: Profile | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateName: (name: string) => void;
}

const STORAGE_KEY = "banking.profile";

const AuthContext = createContext<AuthContextValue | null>(null);

function loadStoredProfile(): Profile | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    const profile = JSON.parse(raw) as Profile;
    const payload = decodeJwt(profile.token);
    if (!payload || isTokenExpired(payload)) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return profile;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

function profileFromToken(token: string, email: string, name?: string): Profile {
  const payload = decodeJwt(token);
  if (!payload) throw new Error("Received an invalid token from the server.");
  return { token, customerId: payload.user.customer_id, userId: payload.user.id, email, name };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(() => loadStoredProfile());

  const persist = useCallback((next: Profile | null) => {
    setProfile(next);
    if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    else localStorage.removeItem(STORAGE_KEY);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await userApi.login(email, password);
      persist(profileFromToken(access_token, email));
    },
    [persist]
  );

  const register = useCallback(
    async (name: string, email: string, phone: string, password: string) => {
      const customer = await customersApi.create({ name, email, phone });
      await userApi.create({ customer_id: customer.id, password });
      const { access_token } = await userApi.login(email, password);
      persist(profileFromToken(access_token, email, name));
    },
    [persist]
  );

  const logout = useCallback(async () => {
    if (profile) {
      try {
        await userApi.logout(profile.token);
      } catch {
        // token may already be invalid/expired - clear local state regardless
      }
    }
    persist(null);
  }, [profile, persist]);

  const updateName = useCallback(
    (name: string) => {
      if (!profile) return;
      persist({ ...profile, name });
    },
    [profile, persist]
  );

  const value = useMemo(
    () => ({ profile, login, register, logout, updateName }),
    [profile, login, register, logout, updateName]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
