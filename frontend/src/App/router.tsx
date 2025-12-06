import { createBrowserRouter, Navigate } from "react-router-dom";
import MainPage from "../Pages/MainPage/MainPage";
import HackDetailsPage from "../Pages/HackDetailsPage/HackDetailsPage";
import ListHackPage from "../Pages/ListHackPage/ListHackPage";

import RequireOrganizerAuth from "../Shared/RequireOrganizerAuth";
import OrganizeAuthPage from "../Pages/OrganizeAuthPage/OrganizeAuthPage";
import OrganizeHackathonPage from "../Pages/OrganizeHackathonPage/OrganizeHackathonPage";
import OrganizeCreateHackPage from "../Pages/OrganizeCreateHackPage/OrganizeCreateHackPage";

import MainLayout from "../Shared/Layouts/MainLayout/MainLayout";
import AuthPage from "../Pages/AuthPage/AuthPage";
import RequireAuth from "../Shared/AuthGuard";

import ParticipantFormPage from '../Pages/ParticipantFormPage/ParticipantFormPage'
import TeamFormPage from '../Pages/TeamFormPage/TeamFormPage'

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
        
      { index: true, element: <Navigate to="/main" replace /> },
      { path: "main", element: <MainPage /> },
      { path: "auth", element: <AuthPage /> },

      {
        element: <RequireAuth />,
        children: [
          { path: "hackdetails/:id", element: <HackDetailsPage /> },
          { path: "listhack", element: <ListHackPage /> },
          { path: "hackdetails/:id/participant-form", element: <ParticipantFormPage /> },
          { path: "hackdetails/:id/team-form", element: <TeamFormPage /> },
        ],
      },
    ],
  },{

    path: "/organizer/login",
    element: <OrganizeAuthPage />,

  },{

    path: "/organizer",
    element: <RequireOrganizerAuth />,
    children: [
      { index: true, element: <Navigate to="/organizer/hacks" replace /> },
      { path: "hacks", element: <OrganizeHackathonPage /> },
      { path: "hacks/create", element: <OrganizeCreateHackPage /> },
      { path: "hacks/:id", element: <OrganizeCreateHackPage /> },
      
    ],
  },

]);