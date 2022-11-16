import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Home, About, Login, ErrorPage, Contactus } from "./pages";
import { ProSidebarProvider } from "react-pro-sidebar";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <ProSidebarProvider>
        <Home />
      </ProSidebarProvider>
    ),
    errorElement: <ErrorPage />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/about",
    element: <About />,
  },
  {
    path: "/contactus",
    element: <Contactus />,
  },
]);

const App = () => <RouterProvider router={router} />;

export default App;
