import { actions } from "./consts";
export const initialState = {
  sellerDetails: {},
  isSellerLoggedIn: false,
};

const authReducer = (state, action) => {
  const { type } = action;

  switch (type) {
    case actions.SELLER_LOGIN:
      return {
        ...state,
        sellerDetails: { name: "Abcd Efgh", city: "Montreal" },
        isSellerLoggedIn: true,
      };

    case actions.SELLER_LOGOUT:
      return { ...state, sellerDetails: {}, isSellerLoggedIn: false };

    default:
      return state;
  }
};

export default authReducer;
