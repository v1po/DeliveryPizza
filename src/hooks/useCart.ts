import { useState, useEffect, useCallback } from 'react';

export type CartItem = {
  id: string;
  title: string;
  price: number;
  imageUrl: string;
  type: string;
  size: number;
  count: number;
};

const calcTotalPrice = (items: CartItem[]): number => {
  return items.reduce((sum, item) => sum + item.price * item.count, 0);
};

const calcTotalCount = (items: CartItem[]): number => {
  return items.reduce((sum, item) => sum + item.count, 0);
};

const getCartFromLS = (): CartItem[] => {
  if (typeof window === 'undefined') return [];
  
  const data = localStorage.getItem('cart');
  return data ? JSON.parse(data) : [];
};

export const useCart = () => {
  const [items, setItems] = useState<CartItem[]>(() => getCartFromLS());
  
  const totalPrice = calcTotalPrice(items);
  const totalCount = calcTotalCount(items);
  
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(items));
  }, [items]);
  
  const addItem = useCallback((item: Omit<CartItem, 'count'>) => {
    setItems(prev => {
      const existingItem = prev.find(cartItem => cartItem.id === item.id);
      
      if (existingItem) {
        return prev.map(cartItem =>
          cartItem.id === item.id
            ? { ...cartItem, count: cartItem.count + 1 }
            : cartItem
        );
      } else {
        return [...prev, { ...item, count: 1 }];
      }
    });
  }, []);
  
  const minusItem = useCallback((id: string) => {
    setItems(prev => {
      const existingItem = prev.find(item => item.id === id);
      
      if (!existingItem) return prev;
      
      if (existingItem.count === 1) {
        return prev.filter(item => item.id !== id);
      } else {
        return prev.map(item =>
          item.id === id
            ? { ...item, count: item.count - 1 }
            : item
        );
      }
    });
  }, []);
  
  const removeItem = useCallback((id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  }, []);
  
  const clearItems = useCallback(() => {
    setItems([]);
  }, []);
  
  const getItemById = useCallback((id: string) => {
    return items.find(item => item.id === id);
  }, [items]);
  
  const setItemCount = useCallback((id: string, count: number) => {
    if (count < 1) {
      removeItem(id);
      return;
    }
    
    setItems(prev =>
      prev.map(item =>
        item.id === id ? { ...item, count } : item
      )
    );
  }, [removeItem]);

  return {
    items,
    totalPrice,
    totalCount,
    
    addItem,
    minusItem,
    removeItem,
    clearItems,
    getItemById,
    setItemCount,
  };
};