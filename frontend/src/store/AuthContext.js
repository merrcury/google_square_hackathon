import { createContext, useReducer, useContext } from "react";
import authReducer, { initialState } from "./AuthReducer";

import { actions } from "./consts";

const AuthContext = createContext(initialState);

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const sellerLogin = () => {
    dispatch({ type: actions.SELLER_LOGIN });
  };

  const sellerLogout = () => {
    dispatch({ type: actions.SELLER_LOGOUT });
  };

  const value = {
    sellerDetails: state.sellerDetails,
    isSellerLoggedIn: state.isSellerLoggedIn,
    sellerLogin,
    sellerLogout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useNotification must be used within ShopContext");
  }

  return context;
};
