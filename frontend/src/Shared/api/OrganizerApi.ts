// OrganizerApi.ts
import {apiInstance} from "../api/apiInstance"; // путь тот же, что в других API

// --- Авторизация ---
export interface OrganizerLoginRequest {
  email: string;
  password: string;
}

export interface Organizer {
  id: string;
  email: string;
  name: string;
}

export interface OrganizerLoginResponse {
  access_token: string;
  token_type: string;
  organizer: Organizer;
}

export const OrganizerApi = {
  login: async (data: OrganizerLoginRequest): Promise<OrganizerLoginResponse> => {
    const res = await apiInstance.post("/organizers/login", data);
    return res.data;
  },
};

// --- Модели хакатонов ---
export interface HackathonCreate {
  title: string;
  description?: string;
  registration_deadline: string;
  tasks_start: string;
  expert_sessions?: string[];
  commission_work: string;
}

export interface HackathonUpdate {
  title?: string;
  description?: string;
  registration_deadline?: string;
  tasks_start?: string;
  expert_sessions?: string[];
  commission_work?: string;
}

export interface HackathonResponse extends HackathonCreate {
  id: string;
  organizer_id: string;
  created_at: string;
  updated_at: string;
  photo_url?: string;
}

export const OrganizerHackApi = {
  getMyHackathons: async (): Promise<HackathonResponse[]> => {
    const res = await apiInstance.get("/organizer/hackathons");
    return res.data;
  },

  createHackathon: async (data: HackathonCreate): Promise<HackathonResponse> => {
    const res = await apiInstance.post("/organizer/hackathons", data);
    return res.data;
  },

  getHackathonById: async (id: string): Promise<HackathonResponse> => {
    const res = await apiInstance.get(`/organizer/hackathons/${id}`);
    return res.data;
  },

  updateHackathon: async (id: string, data: HackathonUpdate) => {
    const res = await apiInstance.patch(`/organizer/hackathons/${id}`, data);
    return res.data;
  },

  uploadPhoto: async (hackathonId: string, file: File) => {
    const form = new FormData();
    form.append("photo", file);

    const res = await apiInstance.post(
      `/organizer/hackathons/${hackathonId}/photo`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    return res.data;
  },

  getHackTeams: async (hackathonId: string) => {
    const res = await apiInstance.get(`/organizer/hackathons/${hackathonId}/teams`);
    return res.data;
  },

  getHackParticipants: async (
    hackathonId: string,
    team_status?: "with_team" | "without_team"
  ) => {
    const res = await apiInstance.get(
      `/organizer/hackathons/${hackathonId}/participants`,
      { params: { team_status } }
    );
    return res.data;
  },
};
