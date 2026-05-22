import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuthContext } from "../../hooks/useAuth";

import './auth.scss';

const CartAuth: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuthContext();
  const navigate = useNavigate();

  const translateMessage = (message: string): string => {
    const normalized = message.toLowerCase();
    if (normalized.includes("field required")) return "Поле обязательно для заполнения.";
    if (normalized.includes("value is not a valid email address")) return "Неверный формат электронной почты.";
    if (normalized.includes("ensure this value has at least")) return "Значение слишком короткое.";
    if (normalized.includes("incorrect email or password")) return "Неправильный email или пароль.";
    if (normalized.includes("invalid credentials")) return "Неверные учетные данные.";
    if (normalized.includes("token has expired")) return "Срок действия токена истек.";
    if (normalized.includes("invalid token")) return "Неверный токен авторизации.";
    return message;
  };

  const parseError = (value: unknown): string => {
    if (!value) return "Ошибка при входе.";
    if (typeof value === "string") return translateMessage(value);
    if (Array.isArray(value)) {
      return value
        .map((item) => {
          if (item && typeof item === "object") {
            return translateMessage(String((item as any).msg || (item as any).message || JSON.stringify(item)));
          }
          return translateMessage(String(item));
        })
        .join(" \n");
    }
    if (typeof value === "object") {
      const msg = (value as any).detail || (value as any).message || JSON.stringify(value);
      return translateMessage(String(msg));
    }
    return translateMessage(String(value));
  };

  const handleSubmit = async () => {
    setError(null);

    if (!email || !password) {
      setError("Введите email и пароль.");
      return;
    }

    try {
      await login({ email, password });
      navigate("/");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(parseError(err.response?.data?.detail ?? err.response?.data?.message));
      } else {
        setError("Ошибка при входе.");
      }
    }
  };

  return (
    <div className='auth'>
      <div className='auth__card'>
        <h2>Добро пожаловать</h2>
        <p className='auth__subtitle'>Войдите, чтобы продолжить заказ и сохранить корзину.</p>
        <div className='auth__card__inputs'>
          <input
            type="email"
            className='username'
            placeholder='Email'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            className='password'
            placeholder='Пароль'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && <p className='auth__error'>{error}</p>}
        <button className="logIn" type="button" onClick={handleSubmit}>
          Войти
        </button>
        <Link to='/signup'>
          <button className='signUp'>Зарегистрироваться</button>
        </Link>
      </div>
    </div>
  );
};

export default CartAuth;
