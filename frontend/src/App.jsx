import { Routes, Route } from "react-router-dom";

import SearchPage from "./pages/SearchPage";
import AdminPage from "./pages/AdminPage";
import Navbar from "./components/Navbar";

function App () {
  return (
    <>
      <Navbar />
      
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </>
  );
}

export default App;