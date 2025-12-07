import { apiInstance } from "./apiInstance";
import type { Skill } from "./UserApi";

export type RoleType =
  | "backend"
  | "frontend"
  | "mobile"
  | "ml"
  | "product"
  | "designer";

export interface Profile {
  id: number;
  user_id: number;
  about?: string | null;
  role: RoleType;
  skills: Skill[];
}

export interface EditProfilePayload {
  user_id: number;
  about?: string | null;
  role: RoleType;
  skills_id: number[];
}

export const ProfileAPI = {
  getProfile: async (userId: number): Promise<Profile> => {
    const { data } = await apiInstance.get(`/api/user/${userId}/profile`);
    return data;
  },

  updateProfile: async (
    profileId: number,
    userId: number,
    payload: EditProfilePayload
  ): Promise<Profile> => {
    const { data } = await apiInstance.put(
      `/api/user/${profileId}/profile?user_id=${userId}`,
      payload
    );
    return data;
  },
};
