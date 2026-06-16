import { createBrowserRouter } from "react-router-dom";
import ChatPage from "../pages/ChatPage";

/**
 * router
 *
 * Central route table.  Add new routes here as the app grows —
 * e.g. an /ingest admin page, a /history page, etc.
 *
 * Usage in main.tsx:
 *   import { router } from "./routes";
 *   <RouterProvider router={router} />
 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <ChatPage />,
  },
  // Future routes:
  // { path: "/ingest", element: <IngestPage /> },
  // { path: "/history", element: <HistoryPage /> },
]);