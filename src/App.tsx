import { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import "./scss/app.scss";
import MainLayout from "./layouts/MainLayout";

const Cart = lazy(() => import(/* webpackChunkName: "Cart" */ "./pages/Cart"));
const FullPizza = lazy(
  () => import(/* webpackChunkName: "FullPizza" */ "./pages/FullPizza")
);
const NotFound = lazy(
  () => import(/* webpackChunkName: "NotFound" */ "./pages/NotFound")
);
const Auth = lazy(() => import(/* webpackChunkName: "Auth" */ "./pages/auth"));
const SignUp = lazy(
  () => import(/* webpackChunkName: "SignUp" */ "./pages/SignUp")
);

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
