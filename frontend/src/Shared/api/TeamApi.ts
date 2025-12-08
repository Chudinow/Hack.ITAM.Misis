import { apiInstance } from "./apiInstance";
import type { RoleType as ProfileRoleType } from "./ProfileApi";

export type RoleType = ProfileRoleType | "никого";

export interface TeamCreatePayload {
  name: string;
  find_roles: RoleType[];
  about: string;
}

export interface TeamResponse {
  id: number;
  name: string;
}

export const TeamAPI = {
  createTeam: async (
    hackId: number | string,
    userId: number,
    payload: TeamCreatePayload
  ): Promise<TeamResponse> => {
    const { data } = await apiInstance.post<TeamResponse>(
      `/api/hack/${hackId}/team/?user_id=${userId}`,
      payload
    );
    return data;
  },

  getUserTeam: async (hackId: number | string, userId: number) => {
    const { data } = await apiInstance.get(
      `/api/hack/${hackId}/team/?user_id=${userId}`
    );
    return data;
  },

  getTeam: async (hackId: number | string, teamId: number | string) => {
    const { data } = await apiInstance.get(
      `/api/hack/${hackId}/team/${teamId}`
    );
    return data;
  },

  searchEmpty: async (hackId: number | string) => {
    const { data } = await apiInstance.get(
      `/api/hack/${hackId}/teams/search`
    );
    return data;
  },

  searchParticipants: async (hackId: number | string) => {
    const { data } = await apiInstance.get(
      `/api/hack/${hackId}/participants/search`
    );
    return data;
  },

  invite: async (hackId: number, teamId: number, participantId: number) => {
    const { data } = await apiInstance.post(
      `/api/hack/${hackId}/team/${teamId}/invite?participant_id=${participantId}`
    );
    return data;
  },

  apply: async (hackId: number, teamId: number, participantId: number) => {
    const { data } = await apiInstance.post(
      `/api/hack/${hackId}/team/${teamId}/apply?participant_id=${participantId}`
    );
    return data;
  },
};
