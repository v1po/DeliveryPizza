import { useState, useCallback, useEffect } from 'react';
import { CartItem, MenuItem } from '../services/types';

interface CartState {
  items: CartItem[];
  totalPrice: number;
  totalCount: number;
}

export const useCart = () => {
  // Загружаем корзину из localStorage при инициализации
  const loadCartFromStorage = (): CartState => {
    if (typeof window === 'undefined') {
      return { items: [], totalPrice: 0, totalCount: 0 };
    }
    
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const parsed = JSON.parse(savedCart);
        // Проверяем корректность структуры
        return {
          items: Array.isArray(parsed.items) ? parsed.items : [],
          totalPrice: typeof parsed.totalPrice === 'number' ? parsed.totalPrice : 0,
          totalCount: typeof parsed.totalCount === 'number' ? parsed.totalCount : 0,
        };
      } catch (error) {
        console.error('Error parsing cart from localStorage:', error);
        return { items: [], totalPrice: 0, totalCount: 0 };
      }
    }
    return { items: [], totalPrice: 0, totalCount: 0 };
  };

  const [cart, setCart] = useState<CartState>(loadCartFromStorage);

  // Сохраняем корзину в localStorage при каждом изменении
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  const addToCart = useCallback((menuItem: MenuItem, quantity: number = 1) => {
    setCart(prev => {
      const currentItems = Array.isArray(prev.items) ? prev.items : [];
      
      const existingItem = currentItems.find(
        item => item.menu_item_id === menuItem.id
      );

      let newItems: CartItem[];
      if (existingItem) {
        newItems = currentItems.map(item =>
          item.menu_item_id === menuItem.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        const cartItem: CartItem = {
          id: `${menuItem.id}-${Date.now()}`,
          menu_item_id: menuItem.id,
          name: menuItem.name,
          price: menuItem.price,
          quantity,
          image_url: menuItem.image_url,
        };
        newItems = [...currentItems, cartItem];
      }

      const totalCount = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      return { items: newItems, totalCount, totalPrice };
    });
  }, []);

  const removeFromCart = useCallback((itemId: string) => {
    setCart(prev => {
      const currentItems = Array.isArray(prev.items) ? prev.items : [];
      const newItems = currentItems.filter(item => item.id !== itemId);
      const totalCount = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      return { items: newItems, totalCount, totalPrice };
    });
  }, []);

  const updateQuantity = useCallback((itemId: string, quantity: number) => {
    setCart(prev => {
      const currentItems = Array.isArray(prev.items) ? prev.items : [];
      const newItems = currentItems.map(item =>
        item.id === itemId ? { ...item, quantity } : item
      );
      const totalCount = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      return { items: newItems, totalCount, totalPrice };
    });
  }, []);

  const clearCart = useCallback(() => {
    setCart({ items: [], totalPrice: 0, totalCount: 0 });
  }, []);

  // Возвращаем гарантированно массив
  return {
    items: Array.isArray(cart.items) ? cart.items : [],
    totalPrice: typeof cart.totalPrice === 'number' ? cart.totalPrice : 0,
    totalCount: typeof cart.totalCount === 'number' ? cart.totalCount : 0,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
  };
};