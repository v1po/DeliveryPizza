import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { CartItem, CartEmpty } from "../../components";
import { selectCart } from "../../redux/cart/selectors";
import { clearItems } from "../../redux/cart/slice";
import { orderService } from "../../services/orderApi";
import { useAuth } from "../../hooks/useAuth";

import "./Cart.scss"; 

const Cart: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { items, totalPrice, totalCount } = useSelector(selectCart);
  
  const { 
    isAuthenticated, 
    user, 
    loading: authLoading, 
    logout,
    checkAuth 
  } = useAuth();

  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successOrderInfo, setSuccessOrderInfo] = useState({
    orderNumber: "",
    totalAmount: 0,
    deliveryAddress: "",
    contactPhone: "",
  });
  
  const [formData, setFormData] = useState({
    delivery_address: "",
    phone_number: "",
    notes: "",
  });

  const onClickClear = () => {
    if (window.confirm("Очистить корзину?")) {
      dispatch(clearItems());
    }
  };

  const handleCheckout = () => {
    if (authLoading) {
      alert("Проверка авторизации...");
      return;
    }

    if (!isAuthenticated) {
      if (
        window.confirm(
          "Для оформления заказа необходимо войти в систему. Перейти на страницу входа?"
        )
      ) {
        navigate("/auth");
      }
      return;
    }

    if (!user) {
      alert("Информация о пользователе не найдена. Пожалуйста, войдите снова.");
      logout();
      navigate("/auth");
      return;
    }

    setShowForm(true);
  };

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.delivery_address.trim() || !formData.phone_number.trim()) {
      alert("Пожалуйста, заполните адрес доставки и телефон");
      return;
    }

    setLoading(true);
    try {
      const orderId = `ORD_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      
      handleSuccessfulOrder(orderId);
      
    } catch (error: any) {
      console.error("Ошибка:", error);
      const fallbackOrderId = `FALLBACK_${Date.now()}`;
      handleSuccessfulOrder(fallbackOrderId);
    } finally {
      setLoading(false);
    }
  };

  const generateLocalOrderId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `LOCAL_${timestamp}_${random}`;
  };

  const handleSuccessfulOrder = (orderId: string) => {
    setSuccessOrderInfo({
      orderNumber: orderId,
      totalAmount: totalPrice,
      deliveryAddress: formData.delivery_address,
      contactPhone: formData.phone_number,
    });

    dispatch(clearItems());

    setShowForm(false);
    setFormData({
      delivery_address: "",
      phone_number: "",
      notes: "",
    });

    setShowSuccessModal(true);
  };

  const handleMockSuccessfulOrder = () => {
    
    const localOrderId = generateLocalOrderId();
    const pendingOrders = JSON.parse(localStorage.getItem("pending_orders") || "[]");
    const newOrder = {
      id: localOrderId,
      items: items.map(item => ({
        id: item.id,
        name: '',
        quantity: item.count,
        price: item.price,
      })),
      delivery_address: formData.delivery_address,
      phone_number: formData.phone_number,
      total_amount: totalPrice,
      created_at: new Date().toISOString(),
      status: "pending_verification",
    };
    
    pendingOrders.push(newOrder);
    localStorage.setItem("pending_orders", JSON.stringify(pendingOrders));
    handleSuccessfulOrder(localOrderId);
  };

  const handleSuccessModalClose = () => {
    setShowSuccessModal(false);
    navigate("/orders");
  };

  const handleCancelOrder = () => {
    setShowForm(false);
    setFormData({
      delivery_address: "",
      phone_number: "",
      notes: "",
    });
  };

  useEffect(() => {
    if (showForm || showSuccessModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [showForm, showSuccessModal]);

  if (authLoading) {
    return (
      <div className="container container--cart">
        <div className="cart">
          <div className="cart__loading">
            <div className="spinner"></div>
            <p>Проверка авторизации...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated && !authLoading && totalCount > 0) {
    return (
      <div className="container container--cart">
        <div className="cart">
          <div className="cart__top">
            <h2 className="content__title">
              <svg
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* SVG path */}
              </svg>
              Корзина
            </h2>
          </div>
          
          <div className="content__items">
            {items.map((item: any) => (
              <CartItem key={item.id} {...item} />
            ))}
          </div>
          
          <div className="cart__bottom">
            <div className="cart__bottom-details">
              <span>
                Всего пицц: <b>{totalCount} шт.</b>
              </span>
              <span>
                Сумма заказа: <b>{totalPrice} ₽</b>
              </span>
            </div>
            
            <div className="cart__auth-required">
              <p>Для оформления заказа требуется авторизация</p>
              <div className="cart__auth-buttons">
                <Link to="/auth" className="button button--outline">
                  <span>Войти</span>
                </Link>
                <Link to="/" className="button button--add">
                  <span>Продолжить покупки</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!totalCount && !showSuccessModal) {
  return <CartEmpty />;
}
  return (
    <>
      <div className="container container--cart">
        <div className="cart">
          <div className="cart__top">
            <h2 className="content__title">
              <svg
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M6.33333 16.3333C7.06971 16.3333 7.66667 15.7364 7.66667 15C7.66667 14.2636 7.06971 13.6667 6.33333 13.6667C5.59695 13.6667 5 14.2636 5 15C5 15.7364 5.59695 16.3333 6.33333 16.3333Z"
                  stroke="white"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M14.3333 16.3333C15.0697 16.3333 15.6667 15.7364 15.6667 15C15.6667 14.2636 15.0697 13.6667 14.3333 13.6667C13.597 13.6667 13 14.2636 13 15C13 15.7364 13.597 16.3333 14.3333 16.3333Z"
                  stroke="white"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M4.78002 4.99999H16.3334L15.2134 10.5933C15.1524 10.9003 14.9854 11.176 14.7417 11.3722C14.4979 11.5684 14.1929 11.6727 13.88 11.6667H6.83335C6.50781 11.6694 6.1925 11.553 5.94689 11.3393C5.70128 11.1256 5.54233 10.8295 5.50002 10.5067L4.48669 2.82666C4.44466 2.50615 4.28764 2.21182 4.04482 1.99844C3.80201 1.78505 3.48994 1.66715 3.16669 1.66666H1.66669"
                  stroke="white"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Корзина
            </h2>
            
            {isAuthenticated && user && (
              <div className="cart__user-info">
                <span>Вы вошли как: {user.email || user.username}</span>
                <button 
                  onClick={() => logout()} 
                  className="button button--outline button--small"
                >
                  Выйти
                </button>
              </div>
            )}
            
            <div onClick={onClickClear} className="cart__clear">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M2.5 5H4.16667H17.5"
                  stroke="#B6B6B6"
                  strokeWidth="1.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M6.66663 5.00001V3.33334C6.66663 2.89131 6.84222 2.46739 7.15478 2.15483C7.46734 1.84227 7.89127 1.66667 8.33329 1.66667H11.6666C12.1087 1.66667 12.5326 1.84227 12.8451 2.15483C13.1577 2.46739 13.3333 2.89131 13.3333 3.33334V5.00001M15.8333 5.00001V16.6667C15.8333 17.1087 15.6577 17.5326 15.3451 17.8452C15.0326 18.1577 14.6087 18.3333 14.1666 18.3333H5.83329C5.39127 18.3333 4.96734 18.1577 4.65478 17.8452C4.34222 17.5326 4.16663 17.1087 4.16663 16.6667V5.00001H15.8333Z"
                  stroke="#B6B6B6"
                  strokeWidth="1.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M8.33337 9.16667V14.1667"
                  stroke="#B6B6B6"
                  strokeWidth="1.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M11.6666 9.16667V14.1667"
                  stroke="#B6B6B6"
                  strokeWidth="1.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span>Очистить корзину</span>
            </div>
          </div>
          
          <div className="content__items">
            {items.map((item: any) => (
              <CartItem key={item.id} {...item} />
            ))}
          </div>
          
          <div className="cart__bottom">
            <div className="cart__bottom-details">
              <span>
                Всего пицц: <b>{totalCount} шт.</b>
              </span>
              <span>
                Сумма заказа: <b>{totalPrice} ₽</b>
              </span>
            </div>
            
            <div className="cart__bottom-buttons">
              <Link to="/" className="button button--outline button--add go-back-btn">
                <svg
                  width="8"
                  height="14"
                  viewBox="0 0 8 14"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M7 13L1 6.93015L6.86175 1"
                    stroke="#D3D3D3"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <span>Вернуться назад</span>
              </Link>
              
              <button
                onClick={handleCheckout}
                className="button pay-btn"
                disabled={items.length === 0}
              >
                <span>
                  {isAuthenticated 
                    ? "Оформить заказ" 
                    : "Войти для оформления"}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Модальное окно оформления заказа */}
      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Оформление заказа</h3>
              
              {user && (
                <div className="modal-user-info">
                  <small>
                    Вы оформляете заказ как: <strong>{user.email || user.username}</strong>
                  </small>
                </div>
              )}
              
              <button onClick={handleCancelOrder} className="modal-close">
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmitOrder}>
              <div className="form-group">
                <label htmlFor="delivery_address">Адрес доставки *</label>
                <input
                  id="delivery_address"
                  type="text"
                  required
                  value={formData.delivery_address}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      delivery_address: e.target.value,
                    })
                  }
                  placeholder="ул. Примерная, д. 1, кв. 1"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone_number">Телефон для связи *</label>
                <input
                  id="phone_number"
                  type="tel"
                  required
                  value={formData.phone_number}
                  onChange={(e) =>
                    setFormData({ ...formData, phone_number: e.target.value })
                  }
                  placeholder="+7 (999) 123-45-67"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">Комментарий к заказу</label>
                <textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) =>
                    setFormData({ ...formData, notes: e.target.value })
                  }
                  placeholder="Дополнительные пожелания (необязательно)"
                  rows={3}
                  disabled={loading}
                />
              </div>

              <div className="order-summary">
                <h4>Итого к оплате:</h4>
                <div className="summary-details">
                  <div>
                    Количество товаров: <strong>{totalCount} шт.</strong>
                  </div>
                  <div>
                    Сумма заказа: <strong>{totalPrice} ₽</strong>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={handleCancelOrder}
                  className="button button--outline"
                  disabled={loading}
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="button pay-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Отправка заказа...
                    </>
                  ) : (
                    `Оплатить ${totalPrice} ₽`
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальное окно успешного оформления */}
      {showSuccessModal && (
        <div className="modal-overlay success-overlay">
          <div className="modal-content success-content">
            <div className="success-header">
              <div className="success-icon">✅</div>
              <h3>Заказ успешно создан!</h3>
            </div>
            
            <div className="success-details">
              <div className="success-row">
                <span>Номер заказа:</span>
                <strong>{successOrderInfo.orderNumber}</strong>
              </div>
              <div className="success-row">
                <span>Сумма заказа:</span>
                <strong>{successOrderInfo.totalAmount} ₽</strong>
              </div>
              <div className="success-row">
                <span>Адрес доставки:</span>
                <span>{successOrderInfo.deliveryAddress}</span>
              </div>
              <div className="success-row">
                <span>Телефон:</span>
                <span>{successOrderInfo.contactPhone}</span>
              </div>
            </div>
            
            <div className="success-message">
              <p>
                <strong>Ваш заказ принят в обработку!</strong>
              </p>
              <p>
                С вами свяжется оператор для подтверждения заказа в ближайшее время.
              </p>
            </div>
            
            <div className="success-actions">
              <button
                onClick={handleSuccessModalClose}
                className="button pay-btn"
              >
                Перейти к моим заказам
              </button>
              
              <button
                onClick={() => {
                  setShowSuccessModal(false);
                  navigate("/");
                }}
                className="button button--outline"
              >
                Вернуться в магазин
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Cart;