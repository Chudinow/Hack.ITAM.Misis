import { createBrowserRouter, Navigate } from "react-router-dom";
import MainPage from "../Pages/MainPage/MainPage";
import HackDetailsPage from "../Pages/HackDetailsPage/HackDetailsPage";
import ListHackPage from "../Pages/ListHackPage/ListHackPage";
import ProfilePage from "../Pages/ProfilePage/ProfilePage";
import OrganizerLayout from "../Shared/Layouts/OrganizerLayout/OrganizerLayout";
import OrganizeAuthPage from "../Pages/OrganizeAuthPage/OrganizeAuthPage";
import OrganizeHackathonPage from "../Pages/OrganizeHackathonPage/OrganizeHackathonPage";
import OrganizeCreateHackPage from "../Pages/OrganizeCreateHackPage/OrganizeCreateHackPage";
import CreateTeamPage from "../Pages/CreateTeamPage/CreateTeamPage";
import MainLayout from "../Shared/Layouts/MainLayout/MainLayout";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <MainLayout />,
        children: [
            { index: true, element: <Navigate to="/main" replace /> },
            { path: "main", element: <MainPage /> },
            { path: "hackdetails", element: <HackDetailsPage /> },
            { path: "listhack", element: <ListHackPage /> },
            { path: "profile", element: <ProfilePage /> },
            { path: "team/create", element: <CreateTeamPage /> },
        ],
    },
    
    {
        path: "/organizer",
        element: <OrganizerLayout />,
        children: [
            { index: true, element: <Navigate to="/organizer/login" replace /> },
            { path: "login", element: <OrganizeAuthPage /> },
            { path: "hacks", element: <OrganizeHackathonPage /> },
            { path: "hacks/create", element: <OrganizeCreateHackPage /> },
            { path: "hacks/:id", element: <OrganizeCreateHackPage /> },
        ],
    },
]);