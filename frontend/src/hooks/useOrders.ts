import { useState, useCallback } from 'react';
import { Order, CreateOrderRequest } from '../services/types';
import { orderService } from '../services/orderApi';

export const useOrders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [currentOrder, setCurrentOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createOrder = useCallback(async (orderData: CreateOrderRequest): Promise<Order | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await orderService.createOrder(orderData);
      
      if (response.success && response.data) {
        const newOrder = response.data;
        setCurrentOrder(newOrder);
        setOrders(prev => [newOrder, ...prev]);
        return newOrder;
      } else {
        throw new Error(response.message || 'Failed to create order');
      }
    } catch (err: any) {
      setError(err.message || 'Error creating order');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getUserOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await orderService.getUserOrders();
      
      if (response.success && response.data) {
        setOrders(response.data);
      } else {
        throw new Error(response.message || 'Failed to fetch orders');
      }
    } catch (err: any) {
      setError(err.message || 'Error fetching orders');
    } finally {
      setLoading(false);
    }
  }, []);

  const getOrderById = useCallback(async (orderId: string): Promise<Order | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await orderService.getOrderById(orderId);
      
      if (response.success && response.data) {
        const order = response.data;
        setCurrentOrder(order);
        return order;
      } else {
        throw new Error(response.message || 'Order not found');
      }
    } catch (err: any) {
      setError(err.message || 'Error fetching order');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCurrentOrder = useCallback(() => {
    setCurrentOrder(null);
  }, []);

  return {
    orders,
    currentOrder,
    loading,
    error,
    createOrder,
    getUserOrders,
    getOrderById,
    clearCurrentOrder,
  };
};