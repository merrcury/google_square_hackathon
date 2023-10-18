import React, { useEffect } from "react";
import { backendAPIInstance } from "../constants/axios";
import { useNavigate } from "react-router-dom";

const SquareRedirect = () => {
  const navigate = useNavigate();
  const getSellerLocationCode = async (token) => {
    const sellerDetails = await backendAPIInstance.post(
      "/seller/get_seller_location",
      {},
      {
        headers: {
          "access-token": token,
        },
      }
    );

    localStorage.removeItem("square_hackathon_seller_location");
    localStorage.setItem(
      "square_hackathon_seller_location",
      sellerDetails.data.location_id
    );
    navigate("/");
  };
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      const requestData = {
        client_id: process.env.REACT_APP_SQUARE_CLIENT_ID,
        code,
        redirect_uri: process.env.REACT_APP_SQUARE_REDIRECT_URI,
        client_secret: process.env.REACT_APP_SQUARE_CLIENT_SECRET,
        grant_type: "authorization_code",
        scopes: [
          "ITEM_READ",
          "ITEM_WRITE",
          "INVENTORY_READ",
          "INVENTORY_WRITE",
          "ORDERS_READ",
          "ORDERS_WRITE",
          "PAYMENTS_READ",
          "PAYMENTS_WRITE",
          "INVOICES_READ",
          "INVOICES_WRITE",
        ],
      };

      fetch(`${process.env.REACT_APP_SQUARE_BASE_URL}/oauth2/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      })
        .then((response) => response.json())
        .then((data) => {
          localStorage.removeItem("square_hackathon_access_token");
          localStorage.setItem(
            "square_hackathon_access_token",
            data.access_token
          );
          getSellerLocationCode(data.access_token);
        })
        .catch((error) => {
          console.log("error in square redirect -->", error);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return <div>SquareRedirect</div>;
};

export default SquareRedirect;
