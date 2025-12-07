import { apiInstance } from "./apiInstance";
import type { RoleType } from "./TeamApi";

export interface Skill {
  id: number;
  name: string;
  type: "hard" | "soft";
}

export interface User {
  id: number;
  name: string;
  photo_url: string;
}

export interface Profile {
  id: number;
  user_id: number;
  about: string;
  role: RoleType;
  skills: Skill[];
}

export interface EditProfilePayload {
  user_id: number;
  about?: string | null;
  role: RoleType;
  skills_id: number[];
}

export const UserAPI = {
  checkAuth: async (): Promise<User> => {
    const { data } = await apiInstance.get("/api/user/auth", {
      withCredentials: true,
    });
    return data;
  },

  authTelegram: async (payload: any): Promise<User> => {
    const { data } = await apiInstance.post("/api/user/auth", payload);
    return data;
  },

  getUser: async (id: number): Promise<User> => {
    const { data } = await apiInstance.get(`/api/user/${id}`);
    return data;
  },

  getProfile: async (id: number): Promise<Profile> => {
    const { data } = await apiInstance.get(`/api/user/${id}/profile`);
    return data;
  },

  updateProfile: async (profileId: number, userId: number, payload: EditProfilePayload) => {
    const { data } = await apiInstance.put(
      `/api/user/${profileId}/profile?user_id=${userId}`,
      payload
    );
    return data;
  },

  getSkills: async (): Promise<Skill[]> => {
    const { data } = await apiInstance.get("/api/skills");
    return data.skills;
  },

  getSkillById: async (skillId: number): Promise<Skill> => {
    const { data } = await apiInstance.get(`/api/skill/${skillId}`);
    return data;
  },
};
