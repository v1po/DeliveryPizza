import axios, { AxiosResponse } from 'axios';
import { CreateOrderRequest, Order, ApiResponse } from './types';

const API_URL = 'http://localhost:8000/api/v1';

export const orderService = {
  createOrder: async (orderData: CreateOrderRequest): Promise<ApiResponse<Order>> => {
    try {
      
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        return {
          success: false,
          message: 'Токен авторизации отсутствует',
          error_code: 'NO_TOKEN'
        };
      }

      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      const response: AxiosResponse<ApiResponse<Order>> = await axios.post(
        `${API_URL}/orders`,
        orderData,
        { headers }
      );

      return response.data;
      
    } catch (error: any) {
      console.error('❌ Ошибка создания заказа:', error);
      
      if (error.response) {
        
        return {
          success: false,
          message: error.response.data?.message || `HTTP ${error.response.status}`,
          error_code: error.response.data?.error_code,
        };
      } else if (error.request) {
        return {
          success: false,
          message: 'Сервер не отвечает',
          error_code: 'NETWORK_ERROR'
        };
      }
      
      return {
        success: false,
        message: error.message || 'Неизвестная ошибка',
      };
    }
  },

  getOrders: async (): Promise<ApiResponse<Order[]>> => {
    try {
      const token = localStorage.getItem('access_token');
      
      const response: AxiosResponse<ApiResponse<Order[]>> = await axios.get(
        `${API_URL}/orders`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('❌ Ошибка получения заказов:', error);
      
      if (error.response?.data) {
        return {
          success: false,
          message: error.response.data.message || 'Ошибка сервера',
          error_code: error.response.data.error_code,
        };
      }
      
      return {
        success: false,
        message: error.message || 'Неизвестная ошибка',
      };
    }
  },

};