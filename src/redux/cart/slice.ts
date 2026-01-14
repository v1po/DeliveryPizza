import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CartItem {
  id: string;
  title: string;
  price: number;
  imageUrl: string;
  type: string;
  size: number;
  count: number;
}

interface CartSliceState {
  items: CartItem[];
  totalPrice: number;
  totalCount: number;
}

const initialState: CartSliceState = {
  items: [],
  totalPrice: 0,
  totalCount: 0,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addItem(state, action: PayloadAction<CartItem>) {
      const findItem = state.items.find(obj => obj.id === action.payload.id);
      
      if (findItem) {
        findItem.count++;
      } else {
        state.items.push({
          ...action.payload,
          count: 1,
        });
      }
      
      state.totalPrice = state.items.reduce((sum, obj) => {
        return (obj.price * obj.count) + sum;
      }, 0);
      
      state.totalCount = state.items.reduce((sum, obj) => {
        return obj.count + sum;
      }, 0);
    },
    
    plusItem(state, action: PayloadAction<string>) {
      const findItem = state.items.find(obj => obj.id === action.payload);
      if (findItem) {
        findItem.count++;
        state.totalPrice = state.items.reduce((sum, obj) => {
          return (obj.price * obj.count) + sum;
        }, 0);
        state.totalCount = state.items.reduce((sum, obj) => {
          return obj.count + sum;
        }, 0);
      }
    },
    
    minusItem(state, action: PayloadAction<string>) {
      const findItem = state.items.find(obj => obj.id === action.payload);
      if (findItem && findItem.count > 1) {
        findItem.count--;
        state.totalPrice = state.items.reduce((sum, obj) => {
          return (obj.price * obj.count) + sum;
        }, 0);
        state.totalCount = state.items.reduce((sum, obj) => {
          return obj.count + sum;
        }, 0);
      }
    },
    
    removeItem(state, action: PayloadAction<string>) {
      state.items = state.items.filter(obj => obj.id !== action.payload);
      state.totalPrice = state.items.reduce((sum, obj) => {
        return (obj.price * obj.count) + sum;
      }, 0);
      state.totalCount = state.items.reduce((sum, obj) => {
        return obj.count + sum;
      }, 0);
    },
    
    clearItems(state) {
      state.items = [];
      state.totalPrice = 0;
      state.totalCount = 0;
    },
  },
});

export const { 
  addItem, 
  plusItem, 
  minusItem, 
  removeItem, 
  clearItems 
} = cartSlice.actions;

export default cartSlice.reducer;