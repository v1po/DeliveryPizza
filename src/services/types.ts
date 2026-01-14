export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  image_url: string;
  available: boolean;
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  id: string;
  menu_item_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
}

export interface OrderItem {
  menu_item_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  menu_item?: MenuItem;
}

export interface Order {
  id: string;
  user_id: string;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  total_amount: number;
  delivery_address: string;
  phone_number: string;
  notes?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface CreateOrderRequest {
  items: Array<{
    product_id: string;  
    quantity: number;
  }>;
  delivery_type: 'delivery' | 'pickup';  
  delivery_address?: string;
  delivery_lat?: number;
  delivery_lng?: number;
  contact_name: string;
  contact_phone: string;
  contact_email?: string;  
  payment_method: 'cash' | 'card' | 'online';  
  customer_note?: string; 
  promo_code?: string; 
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  address?: string;
  phone?: string; 
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error_code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
