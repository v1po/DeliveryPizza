import React, { useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './styles/RegisterOrder.css';

const OrderSuccess: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const orderDetails = location.state?.orderDetails;

  useEffect(() => {
    if (!orderDetails) {
      navigate('/');
    }
  }, [orderDetails, navigate]);

  if (!orderDetails) {
    return null;
  }

  return (
    <div className="register-order-container">
      <div className="success-container">
        <div className="success-icon">🎉</div>
        
        <h1>Заказ успешно оформлен!</h1>
        
        <p className="success-message">
          Спасибо за ваш заказ! Мы уже начали его готовить.
        </p>
        
        <div className="order-details-card">
          <h2>Детали заказа</h2>
          
          <div className="order-info">
            <div className="info-row">
              <span className="info-label">Номер заказа:</span>
              <span className="info-value">{orderDetails.orderNumber}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Имя:</span>
              <span className="info-value">{orderDetails.customerName}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Адрес доставки:</span>
              <span className="info-value">{orderDetails.deliveryAddress}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Время доставки:</span>
              <span className="info-value">{orderDetails.deliveryTime}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Способ оплаты:</span>
              <span className="info-value">{orderDetails.paymentMethod}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Примерное время доставки:</span>
              <span className="info-value">{orderDetails.estimatedDelivery}</span>
            </div>
            
            <div className="info-row total">
              <span className="info-label">Сумма заказа:</span>
              <span className="info-value">{orderDetails.totalAmount} ₽</span>
            </div>
          </div>
        </div>
        
        <div className="next-steps">
          <h3>Что дальше?</h3>
          <ul className="steps-list">
            <li>✅ Заказ принят в обработку</li>
            <li>⏳ Начинаем готовить вашу пиццу</li>
            <li>🚗 Курьер отправится к вам в назначенное время</li>
            <li>📱 Мы отправим SMS с номером курьера</li>
          </ul>
        </div>
        
        <div className="success-actions">
          <Link to="/orders" className="btn-primary">
            Посмотреть мои заказы
          </Link>
          
          <Link to="/" className="btn-secondary">
            Вернуться в меню
          </Link>
          
          <div className="support-info">
            <p>Вопросы по заказу?</p>
            <a href="tel:+78001234567" className="support-phone">
              📞 8 (800) 123-45-67
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccess;