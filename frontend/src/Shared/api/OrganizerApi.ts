// src/Shared/api/OrganizerApi.ts
import { apiInstance } from "./apiInstance";

/* ==========
   TYPES
========== */

// auth
export interface OrganizerLoginPayload {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface OrganizerResponse {
  id: number;
  login: string;
}

// hackathons
export interface HackathonCreate {
  name: string;
  description: string;
  start_date: string; // YYYY-MM-DD
  end_date: string;   // YYYY-MM-DD
  tags?: string;
  max_teams?: number;
  min_team_size?: number;
  max_team_size?: number;
}

export interface HackathonUpdate {
  name?: string | null;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  tags?: string | null;
  max_teams?: number | null;
  min_team_size?: number | null;
  max_team_size?: number | null;
}

export interface HackathonResponse {
  id: number;
  name: string;
  description: string;
  start_date: string;  // date
  end_date: string;    // date
  tags: string;
  max_teams: number;
  min_team_size: number;
  max_team_size: number;
  organizer_id: number;
  photo_url: string | null;
  created_at: string;
}

// teams / participants / analytics
export interface TeamMemberShort {
  user_id: number;
  name: string;
  role: string | null;
  approved: boolean;
  avatar_url?: string | null;
}

export interface TeamOrgResponse {
  id: number;
  name: string;
  approved: boolean;
  members: TeamMemberShort[];
}

export interface TeamApproveResponse {
  team_id: number;
  approved: boolean;
}

export interface ParticipantResponse {
  user_id: number;
  name: string;
  avatar_url: string;
  has_team: boolean;
  team_name: string | null;
  role: string | null;
  skills: string[];
}

export interface AnalyticsResponse {
  total_teams: number;
  approved_teams: number;
  total_participants: number;
  participants_with_team: number;
  participants_without_team: number;
}

/* ==========
   API
========== */

export const OrganizerApi = {
  /* --- AUTH --- */

  login: async (payload: OrganizerLoginPayload): Promise<Token> => {
    const { data } = await apiInstance.post<Token>("/organizer/login", payload);
    // backend сам ставит HttpOnly куки, мы их НЕ трогаем
    return data;
  },

  me: async (): Promise<OrganizerResponse> => {
    const { data } = await apiInstance.get<OrganizerResponse>("/organizer/me");
    return data;
  },

  logout: async (): Promise<void> => {
    await apiInstance.post("/organizer/logout");
  },

  /* --- HACKATHONS --- */

  getMyHackathons: async (): Promise<HackathonResponse[]> => {
    const { data } = await apiInstance.get<HackathonResponse[]>(
      "/organizer/hackathons/"
    );
    return data;
  },

  createHackathon: async (
    payload: HackathonCreate
  ): Promise<HackathonResponse> => {
    const { data } = await apiInstance.post<HackathonResponse>(
      "/organizer/hackathons/",
      payload
    );
    return data;
  },

  updateHackathon: async (
    hackathonId: number | string,
    payload: HackathonUpdate
  ): Promise<HackathonResponse> => {
    const { data } = await apiInstance.patch<HackathonResponse>(
      `/organizer/hackathons/${hackathonId}`,
      payload
    );
    return data;
  },

  getHackathonById: async (
    hackathonId: number | string
  ): Promise<HackathonResponse> => {
    const { data } = await apiInstance.get<HackathonResponse>(
      `/organizer/hackathons/${hackathonId}`
    );
    return data;
  },

  uploadPhoto: async (
    hackathonId: number | string,
    file: File
  ): Promise<void> => {
    const formData = new FormData();
    formData.append("photo", file);

    await apiInstance.post(
      `/organizer/hackathons/${hackathonId}/photo`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
  },

  /* --- TEAMS / PARTICIPANTS / ANALYTICS --- */

  getHackathonTeams: async (
    hackathonId: number | string
  ): Promise<TeamOrgResponse[]> => {
    const { data } = await apiInstance.get<TeamOrgResponse[]>(
      `/organizer/hackathons/${hackathonId}/teams`
    );
    return data;
  },

  getHackathonParticipants: async (
    hackathonId: number | string,
    teamStatus?: string | null
  ): Promise<ParticipantResponse[]> => {
    const { data } = await apiInstance.get<ParticipantResponse[]>(
      `/organizer/hackathons/${hackathonId}/participants`,
      {
        params: teamStatus ? { team_status: teamStatus } : undefined,
      }
    );
    return data;
  },

  approveTeam: async (
    hackathonId: number | string,
    teamId: number,
    approve: boolean = true
  ): Promise<TeamApproveResponse> => {
    const { data } = await apiInstance.post<TeamApproveResponse>(
      `/organizer/hackathons/${hackathonId}/teams/${teamId}/approve`,
      null,
      { params: { approve } }
    );
    return data;
  },

  assignParticipant: async (
    hackathonId: number | string,
    userId: number,
    teamId: number,
    role: string
  ) => {
    const { data } = await apiInstance.post(
      `/organizer/hackathons/${hackathonId}/participants/${userId}/assign`,
      null,
      {
        params: { team_id: teamId, role },
      }
    );
    return data;
  },

  getAnalytics: async (
    hackathonId: number | string
  ): Promise<AnalyticsResponse> => {
    const { data } = await apiInstance.get<AnalyticsResponse>(
      `/organizer/hackathons/${hackathonId}/analytics`
    );
    return data;
  },

  exportTeamsCsv: async (hackathonId: number | string): Promise<Blob> => {
    const { data } = await apiInstance.get(
      `/organizer/hackathons/${hackathonId}/export/csv`,
      { responseType: "blob" }
    );
    return data as Blob;
  },
};
