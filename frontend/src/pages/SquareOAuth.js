import React from "react";

import { Box, Button, Text } from "@chakra-ui/react";
// import { useAuth } from "../store/AuthContext";

const SquareOAuth = () => {
  // const { sellerLogin } = useAuth();

  const CLIENT_ID = process.env.REACT_APP_SQUARE_CLIENT_ID;
  const REDIRECT_URI = process.env.REACT_APP_SQUARE_REDIRECT_URI;
  const BASE_URL = process.env.REACT_APP_SQUARE_BASE_URL;

  const handleLoginClick = () => {
    const authorizationUrl = `${BASE_URL}/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=ITEMS_READ ITEMS_WRITE INVENTORY_READ INVENTORY_WRITE ORDERS_READ ORDERS_WRITE PAYMENTS_READ PAYMENTS_WRITE INVOICES_READ INVOICES_WRITE CUSTOMERS_READ CUSTOMERS_WRITE EMPLOYEES_READ EMPLOYEES_WRITE MERCHANT_PROFILE_READ MERCHANT_PROFILE_WRITE`;
    window.location.href = authorizationUrl;
  };

  return (
    <Box
      background="linear-gradient(to right, #91EAE4, #86A8E7, #7F7FD5)"
      width="100vw"
      height="100vh" // Increase the height to make the box larger
      display="flex"
      justifyContent="center"
      alignItems="center"
    >
      <Box
        p="4"
        bgColor="white"
        borderRadius="md"
        boxShadow="lg"
        textAlign="center"
      >
        <Text fontSize="xl" fontWeight="bold" mb="4">
          Seller AI
        </Text>
        <Button
          colorScheme="blue"
          onClick={() => {
            handleLoginClick();
          }}
        >
          Login with Square
        </Button>
      </Box>
    </Box>
  );
};

export default SquareOAuth;
