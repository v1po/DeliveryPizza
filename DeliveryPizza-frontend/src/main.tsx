import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { CartProvider } from "./hooks/useCartContext";
import { FilterProvider } from "./hooks/useFilterContext";
import { AuthProvider } from "./hooks/useAuth";

const rootElem = document.getElementById("root");

if (rootElem) {
  const root = ReactDOM.createRoot(rootElem);

  root.render(
    <BrowserRouter>
      <AuthProvider>
        <FilterProvider>
          <CartProvider>
            <App />
          </CartProvider>
        </FilterProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
