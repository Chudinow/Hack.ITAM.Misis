import { apiInstance } from "./apiInstance";

/* ===============================
      TYPES (из Swagger)
================================= */

/* --- Telegram Auth Payload --- */
export interface TelegramAuthPayload {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  photo_url: string;
  auth_date: number;
  hash: string;
}

/* --- User (basic info) --- */
export interface User {
  id: number;
  name: string;
  photo_url: string;
}

/* --- Profile Edit Payload --- */
export interface UserProfileEditPayload {
  user_id: number;
  about: string;
  skills_id: number[];
  role: string; // новое поле
}

/* --- Skill --- */
export interface Skill {
  id: number;
  name: string;
  type: "hard" | "soft";
}

/* --- User Profile (GET user/{id}/profile) --- */
export interface UserProfile {
  id: number;
  user_id: number;
  about: string;
  skills: Skill[];
  role: string; // новое поле
}

/* --- Skills List --- */
export interface SkillsListResponse {
  skills: Skill[];
}

/* ====================================
          USER API METHODS
===================================== */

export const UserAPI = {
  /**
   * Telegram авторизация
   * POST /api/user/auth
   */
  authTelegram: async (payload: TelegramAuthPayload): Promise<User> => {
    const { data } = await apiInstance.post<User>("/api/user/auth", payload);
    return data;
  },

  /**
   * Получить пользователя по ID
   * GET /api/user/{user_id}
   */
  getUser: async (userId: number | string): Promise<User> => {
    const { data } = await apiInstance.get<User>(`/api/user/${userId}`);
    return data;
  },

  /**
   * Получить профиль пользователя
   * GET /api/user/{user_id}/profile
   */
  getProfile: async (userId: number | string): Promise<UserProfile> => {
    const { data } = await apiInstance.get<UserProfile>(
      `/api/user/${userId}/profile`
    );
    return data;
  },

  /**
   * Изменить профиль пользователя
   * PUT /api/user/{user_id}/profile
   */
  updateProfile: async (
    userId: number | string,
    payload: UserProfileEditPayload
  ): Promise<UserProfile> => {
    const { data } = await apiInstance.put<UserProfile>(
      `/api/user/${userId}/profile`,
      payload
    );
    return data;
  },

  /**
   * Список всех навыков
   * GET /api/user/profile/skills
   */
  getSkills: async (): Promise<SkillsListResponse> => {
    const { data } = await apiInstance.get<SkillsListResponse>(
      "/api/user/profile/skills"
    );
    return data;
  },

  /**
   * Получить навык по ID
   * GET /api/user/profile/skills/{skill_id}
   */
  getSkillById: async (skillId: number | string): Promise<Skill> => {
    const { data } = await apiInstance.get<Skill>(
      `/api/user/profile/skills/${skillId}`
    );
    return data;
  },
};
