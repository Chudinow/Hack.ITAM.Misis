import { apiInstance } from "./apiInstance";

/* ===============================
        TYPES (из Swagger)
================================= */

/* --- член команды при создании --- */
export interface TeamMemberCreate {
  user_id: number;
  role: string; // backend | frontend | design | etc.
}

/* --- тело запроса для создания команды --- */
export interface TeamCreatePayload {
  name: string;
  hackathon_id: number;
  member_ids: TeamMemberCreate[];
  is_completed: boolean;
}

/* --- структура участника команды в ответе API --- */
export interface TeamMember {
  id: number;
  user_id: number;
  role: string;
  approved: boolean;
}

/* --- структура команды --- */
export interface Team {
  id: number;
  name: string;
  hackathon_id: number;
  is_completed: boolean;
  members: TeamMember[];
}

/* --- структура команды при поиске empty --- */
export interface EmptyTeam {
  id: number;
  name: string;
  hackathon_id: number;
  is_completed: boolean;
  empty_roles: {
    role: string;
  }[];
}

/* ===============================
          TEAM API
================================= */

export const TeamAPI = {
  /**
   * Создать команду
   * POST /api/hack/{hack_id}/team/
   */
  createTeam: async (
    hackId: number | string,
    payload: TeamCreatePayload
  ): Promise<Team> => {
    const { data } = await apiInstance.post<Team>(
      `/api/hack/${hackId}/team/`,
      payload
    );
    return data;
  },

  /**
   * Получить команду по ID
   * GET /api/hack/{hack_id}/team/{team_id}
   */
  getTeam: async (
    hackId: number | string,
    teamId: number | string
  ): Promise<Team> => {
    const { data } = await apiInstance.get<Team>(
      `/api/hack/${hackId}/team/${teamId}`
    );
    return data;
  },

  /**
   * Найти команды с пустыми ролями
   * GET /api/hack/{hack_id}/team/search/empty
   */
  getEmptyTeams: async (
    hackId: number | string
  ): Promise<EmptyTeam[]> => {
    const { data } = await apiInstance.get<EmptyTeam[]>(
      `/api/hack/${hackId}/team/search/empty`
    );
    return data;
  }
};
