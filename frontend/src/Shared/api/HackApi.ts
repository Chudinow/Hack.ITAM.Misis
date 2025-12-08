import { apiInstance } from "./apiInstance";

export interface Hack {
  id: number;
  name: string;
  description: string;
  photo_url: string;
  start_date: string;
  end_date: string;
  tags: string;
}

export interface HackListMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface HackListResponse {
  hacks: Hack[];
  meta: HackListMeta;
}

export const HackAPI = {
  getById: async (hackId: number | string): Promise<Hack> => {
    const { data } = await apiInstance.get<Hack>(`/api/hack/${hackId}`);
    return data;
  },

  getAll: async (
    page = 1,
    per_page = 20
  ): Promise<HackListResponse> => {
    const { data } = await apiInstance.get<HackListResponse>(
      "/api/hacks/all",
      { params: { page, per_page } }
    );
    return data;
  },

  getUpcoming: async (): Promise<HackListResponse> => {
    const { data } = await apiInstance.get<HackListResponse>(
      "/api/hacks/upcoming"
    );
    return data;
  },
};
