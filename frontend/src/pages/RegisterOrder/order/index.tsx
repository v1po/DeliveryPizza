import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { selectCart } from '../../../redux/cart/selectors';
import { clearItems } from '../../../redux/cart/slice';
import { CreateOrderRequest } from '../../../services/types';
import { orderService } from '../../../services/orderApi';
import './styles/RegisterOrder.css';

const RegisterOrder: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  
  const { items, totalPrice, totalCount } = useSelector(selectCart);
  
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    delivery_address: '',
    delivery_time: 'asap',
    payment_method: 'cash',
    notes: '',
  });

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        
        setFormData(prev => ({
          ...prev,
          full_name: parsedUser.first_name || parsedUser.full_name || '',
          email: parsedUser.email || '',
          phone: parsedUser.phone || '',
        }));
      } catch (error) {
        console.error('Ошибка загрузки данных пользователя:', error);
      }
    }
  }, []);

  useEffect(() => {
    if (items.length === 0 && !location.state?.fromCheckout) {
      navigate('/cart');
    }
  }, [items, navigate, location]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!formData.full_name.trim()) {
    alert('Пожалуйста, введите ваше имя');
    return;
  }
  
  if (!formData.phone.trim()) {
    alert('Пожалуйста, введите номер телефона');
    return;
  }
  
  if (!formData.delivery_address.trim()) {
    alert('Пожалуйста, введите адрес доставки');
    return;
  }

  setLoading(true);

  try {
  const orderData: CreateOrderRequest = {
  delivery_address: formData.delivery_address,
  contact_phone: formData.phone,
  contact_name: formData.full_name,
  payment_method: 'card',
  delivery_type: 'delivery' as const, 
  items: items.map(item => ({
    product_id: item.id.toString(),
    quantity: item.count,
  })),
};

    const response = await orderService.createOrder(orderData);
    
  } catch (error: any) {

  } finally {
    setLoading(false);
  }
};

  const getEstimatedDeliveryTime = () => {
    if (formData.delivery_time === 'asap') {
      const now = new Date();
      now.setMinutes(now.getMinutes() + 45); 
      return now.toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
    return formData.delivery_time;
  };

  const handleBackToCart = () => {
    navigate('/cart');
  };

  if (items.length === 0) {
    return (
      <div className="empty-cart-container">
        <div className="empty-cart-content">
          <h2>Корзина пуста</h2>
          <p>Пожалуйста, добавьте товары в корзину для оформления заказа</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Вернуться в меню
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="register-order-container">
      <div className="register-order-header">
        <h1>Оформление заказа</h1>
        <div className="order-steps">
          <div className="step active">1. Корзина</div>
          <div className="step active">2. Данные заказа</div>
          <div className="step">3. Подтверждение</div>
        </div>
      </div>

      <div className="register-order-content">
        <div className="order-form-section">
          <h2>Данные для доставки</h2>
          
          <form onSubmit={handleSubmit} className="order-form">
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="full_name">Ваше имя *</label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="Иван Иванов"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="example@mail.com"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Телефон *</label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="+7 (999) 123-45-67"
                  disabled={loading}
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="delivery_address">Адрес доставки *</label>
                <input
                  id="delivery_address"
                  name="delivery_address"
                  type="text"
                  required
                  value={formData.delivery_address}
                  onChange={handleInputChange}
                  placeholder="ул. Примерная, д. 1, кв. 1, подъезд 2, этаж 3"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="delivery_time">Время доставки</label>
                <select
                  id="delivery_time"
                  name="delivery_time"
                  value={formData.delivery_time}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="asap">Как можно скорее (~45 мин)</option>
                  <option value="13:00">13:00 - 14:00</option>
                  <option value="14:00">14:00 - 15:00</option>
                  <option value="15:00">15:00 - 16:00</option>
                  <option value="16:00">16:00 - 17:00</option>
                  <option value="17:00">17:00 - 18:00</option>
                  <option value="18:00">18:00 - 19:00</option>
                  <option value="19:00">19:00 - 20:00</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="payment_method">Способ оплаты</label>
                <select
                  id="payment_method"
                  name="payment_method"
                  value={formData.payment_method}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="cash">Наличными курьеру</option>
                  <option value="card">Картой онлайн</option>
                  <option value="card_courier">Картой курьеру</option>
                </select>
              </div>

              <div className="form-group full-width">
                <label htmlFor="notes">Комментарий к заказу</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  placeholder="Дополнительные пожелания, особенности доставки и т.д."
                  rows={3}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                type="button"
                onClick={handleBackToCart}
                className="btn-secondary"
                disabled={loading}
              >
                ← Назад к корзине
              </button>
              
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Оформляем заказ...
                  </>
                ) : (
                  `Оформить заказ за ${totalPrice} ₽`
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="order-summary-section">
          <div className="order-summary-card">
            <h3>Ваш заказ</h3>
            
            <div className="order-items">
              {items.map((item: any) => (
                <div key={item.id} className="order-item">
                  <div className="item-info">
                    <span className="item-name">{item.title}</span>
                    <span className="item-details">
                      {item.type}, {item.size} см.
                    </span>
                  </div>
                  <div className="item-quantity-price">
                    <span className="item-quantity">{item.count} шт.</span>
                    <span className="item-price">{item.price * item.count} ₽</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="order-totals">
              <div className="total-row">
                <span>Товары ({totalCount} шт.)</span>
                <span>{totalPrice} ₽</span>
              </div>
              
              <div className="total-row">
                <span>Доставка</span>
                <span>Бесплатно</span>
              </div>
              
              <div className="total-row final">
                <span>Итого к оплате</span>
                <span className="total-amount">{totalPrice} ₽</span>
              </div>
            </div>

            <div className="delivery-info">
              <h4>Информация о доставке</h4>
              <div className="info-item">
                <span className="info-label">Адрес:</span>
                <span className="info-value">
                  {formData.delivery_address || 'Не указан'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Время:</span>
                <span className="info-value">
                  {formData.delivery_time === 'asap' 
                    ? 'Как можно скорее (~45 мин)' 
                    : `На ${formData.delivery_time}`}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Оплата:</span>
                <span className="info-value">
                  {formData.payment_method === 'cash' 
                    ? 'Наличными курьеру' 
                    : formData.payment_method === 'card'
                    ? 'Картой онлайн'
                    : 'Картой курьеру'}
                </span>
              </div>
            </div>
          </div>

          <div className="customer-support">
            <h4>Нужна помощь?</h4>
            <p>Если у вас возникли вопросы по оформлению заказа:</p>
            <div className="support-contacts">
              <a href="tel:+78001234567" className="support-link">
                📞 8 (800) 123-45-67
              </a>
              <a href="mailto:support@pizza.ru" className="support-link">
                ✉️ support@pizza.ru
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterOrder;