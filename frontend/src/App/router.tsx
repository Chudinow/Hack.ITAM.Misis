import { createBrowserRouter, Navigate } from "react-router-dom";
import MainLayout from "../Shared/Layouts/MainLayout/MainLayot";
import MainPage from "../Pages/MainPage/MainPage";
import HackDetailsPage from "../Pages/HackDetailsPage/HackDetailsPage";
import ListHackPage from "../Pages/ListHackPage/ListHackPage";
import ProfilePage from "../Pages/ProfilePage/ProfilePage";

export const router = createBrowserRouter([
    {
        path:"/",
        element:<MainLayout/>,
        children:[
            {index: true, element:<Navigate to="/main" replace/>},
            {path:"main", element:<MainPage/>},
            {path:"hackdetails",element:<HackDetailsPage/>},
            {path:"listhack",element:<ListHackPage/>},
            {path:"profile",element:<ProfilePage/>},
            
        ]
    }
])