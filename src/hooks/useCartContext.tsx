import React from "react";
import { useCart } from "./useCart";
import type { CartItem } from "../types/cart";
import { useContext } from "react";

type CartContextType = ReturnType<typeof useCart>;

const CartContext = React.createContext<CartContextType | null>(null);

export const CartProvider: React.FC<React.PropsWithChildren<{}>> = ({
  children,
}) => {
  const cart = useCart();

  return <CartContext.Provider value={cart}>{children}</CartContext.Provider>;
};

export const useCartContext = (): CartContextType => {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error("");
  }
  return ctx;
};

export type { CartItem };
