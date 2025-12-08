import { apiInstance } from "./apiInstance";
import type { RoleType } from "./ProfileApi";
import type { Profile } from "./ProfileApi";

export interface Skill {
  id: number;
  name: string;
  type: "hard" | "soft";
}

export interface TelegramAuthPayload {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface User {
  id: number;
  name: string;
  photo_url: string;
}

export interface EditProfilePayload {
  user_id: number;
  about?: string | null;
  role: RoleType;
  skills_id: number[];
}

export const UserAPI = {
  // Проверка авторизации (используется в RequireAuth)
  checkAuth: async (): Promise<User> => {
    const { data } = await apiInstance.get<User>("/api/user/auth", {
      withCredentials: true,
    });
    return data;
  },

  // Телеграм авторизация
  authTelegram: async (payload: TelegramAuthPayload): Promise<User> => {
    const { data } = await apiInstance.post<User>("/api/user/auth", payload);
    return data;
  },

  // Базовый юзер
  getUser: async (id: number): Promise<User> => {
    const { data } = await apiInstance.get<User>(`/api/user/${id}`);
    return data;
  },

  // Профиль пользователя (дублирует ProfileAPI, но типизирован тем же Profile)
  getProfile: async (id: number): Promise<Profile> => {
    const { data } = await apiInstance.get<Profile>(`/api/user/${id}/profile`);
    return data;
  },

  updateProfile: async (
    profileId: number,
    userId: number,
    payload: EditProfilePayload
  ): Promise<Profile> => {
    const { data } = await apiInstance.put<Profile>(
      `/api/user/${profileId}/profile?user_id=${userId}`,
      payload
    );
    return data;
  },

  // Список всех навыков
  getSkills: async (): Promise<Skill[]> => {
    const { data } = await apiInstance.get<{ skills: Skill[] }>("/api/skills");
    return data.skills;
  },

  getSkillById: async (skillId: number): Promise<Skill> => {
    const { data } = await apiInstance.get<Skill>(`/api/skill/${skillId}`);
    return data;
  },
};
