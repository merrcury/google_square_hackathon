import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import SquareOAuth from "./pages/SquareOAuth";
import CatalogList from "./pages/CatalogList";
import IngredientForm from "./pages/IngredientForm";
import Inventory from "./pages/Inventory";
import Chat from "./pages/Chat";
import RecommendMenu from "./pages/RecommendMenu";
import IngredientsList from "./pages/IngredientsList";
import { useNavigate } from "react-router-dom";
import { Wrapper } from "./components/Wrapper";
import SquareRedirect from "./pages/SquareRedirect";

function App() {
  const token = localStorage.getItem("square_hackathon_access_token");
  const locationId = localStorage.getItem("square_hackathon_seller_location");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token && !locationId) {
      navigate("/login");
    }
  }, [token, locationId, navigate]);

  return (
    <ChakraProvider>
      <div className="App">
        <Routes>
          {!token && !locationId && (
            <>
              <Route path="/login" element={<SquareOAuth />} />
              <Route path="/auth/v1/callback" element={<SquareRedirect />} />
            </>
          )}
          {token && locationId && (
            <Route path="/" element={<Wrapper />}>
              <Route path="/" element={<IngredientsList />} />
              <Route path="/add-ingredients" element={<IngredientForm />} />
              <Route path="/recommend-menu" element={<RecommendMenu />} />
              <Route path="/catalogs" element={<CatalogList />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/chat" element={<Chat />} />
            </Route>
          )}
        </Routes>
      </div>
    </ChakraProvider>
  );
}

export default App;
