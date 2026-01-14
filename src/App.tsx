import Loadable from 'react-loadable';
import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import './scss/app.scss';
import MainLayout from './layouts/MainLayout';

const Cart = React.lazy(() => import(/* webpackChunkName: "Cart" */ './pages/Cart'));
const FullPizza = React.lazy(() => import(/* webpackChunkName: "FullPizza" */ './pages/FullPizza'));
const NotFound = React.lazy(() => import(/* webpackChunkName: "NotFound" */ './pages/NotFound'));
const Auth = React.lazy(() => import(/* webpackChunkName: "Auth" */ './pages/auth'));
const SignUp = React.lazy(() => import(/* webpackChunkName: "SignUp" */ './pages/SignUp'));
const RegisterOrder = React.lazy(() => import(/* webpackChunkName: "RegisterOrder" */ './pages/RegisterOrder/order'));
const OrderSuccess = React.lazy(() => import(/* webpackChunkName: "OrderSuccess" */ './pages/RegisterOrder/orderSuccess'));

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route path="" element={<Home />} />
        <Route
          path="cart"
          element={
            <Suspense fallback={<div>Идёт загрузка корзины...</div>}>
              <Cart />
            </Suspense>
          }
        />
        <Route
          path="pizza/:id"
          element={
            <Suspense fallback={<div>Идёт загрузка...</div>}>
              <FullPizza />
            </Suspense>
          }
        />
        
        <Route
          path="checkout"
          element={
            <Suspense fallback={<div>Загружаем страницу оформления...</div>}>
              <RegisterOrder />
            </Suspense>
          }
        />
        <Route
          path="order-success"
          element={
            <Suspense fallback={<div>Загружаем...</div>}>
              <OrderSuccess />
            </Suspense>
          }
        />
        
        <Route
          path="auth"
          element={
            <Suspense fallback={<div>Идёт загрузка...</div>}>
              <Auth />
            </Suspense>
          }
        />
        <Route
          path="signup"
          element={
            <Suspense fallback={<div>Идёт загрузка...</div>}>
              <SignUp />
            </Suspense>
          }
        />
        
        <Route
          path="*"
          element={
            <Suspense fallback={<div>Идёт загрузка...</div>}>
              <NotFound />
            </Suspense>
          }
        />
      </Route>
    </Routes>
  );
}

export default App;