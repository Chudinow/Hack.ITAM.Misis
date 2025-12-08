import { apiInstance } from "./apiInstance";
import type { Skill } from "./UserApi";

export type RoleType =
  |"никого"
  | "backend"
  | "frontend"
  | "mobile"
  | "ml"
  | "product"
  | "designer";

export interface Profile {
  id: number;
  user_id: number;
  about: string | null;
  role: RoleType | null;
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
    const { data } = await apiInstance.get<Profile>(
      `/api/user/${userId}/profile`
    );
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
};
