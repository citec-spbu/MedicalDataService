import { configureStore } from "@reduxjs/toolkit";
import cartReducer from "./cart";
import { useSelector, useDispatch, TypedUseSelectorHook } from "react-redux";

export const store = configureStore({
  reducer: {
    cart: cartReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type CartDispatch = typeof store.dispatch;

export const useCartDispatch = () => useDispatch<CartDispatch>();
export const useCartSelector: TypedUseSelectorHook<RootState> = useSelector;
