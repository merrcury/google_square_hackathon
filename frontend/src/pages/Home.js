import React from "react";

import { Box, Text } from "@chakra-ui/react";
import { useAuth } from "../store/AuthContext";

const Home = () => {
  const { sellerDetails } = useAuth();

  return (
    <div>
      <Box
        p="4"
        bgColor="white"
        borderRadius="md"
        boxShadow="lg"
        textAlign="center"
      >
        <Text fontSize="xl" fontWeight="bold" mb="4">
          Welcome to the Homepage
        </Text>
        {sellerDetails && (
          <div>
            <p>Welcome, {sellerDetails.name}!</p>
            <p>City: {sellerDetails.city}</p>
            <p>Email: {sellerDetails.email}</p>
          </div>
        )}
      </Box>
    </div>
  );
};

export default Home;
