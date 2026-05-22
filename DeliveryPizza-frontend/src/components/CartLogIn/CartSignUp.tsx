import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuthContext } from "../../hooks/useAuth";

import './SignUp.scss';

const CartSignUp: React.FC = () => {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { register } = useAuthContext();
  const navigate = useNavigate();

  const translateMessage = (message: string): string => {
    const normalized = message.toLowerCase();
    if (normalized.includes("field required")) return "Поле обязательно для заполнения.";
    if (normalized.includes("value is not a valid email address")) return "Неверный формат электронной почты.";
    if (normalized.includes("ensure this value has at least")) return "Значение слишком короткое.";
    if (normalized.includes("must contain at least one uppercase letter")) return "Пароль должен содержать заглавную букву.";
    if (normalized.includes("must contain at least one lowercase letter")) return "Пароль должен содержать строчную букву.";
    if (normalized.includes("must contain at least one digit")) return "Пароль должен содержать цифру.";
    if (normalized.includes("passwords do not match")) return "Пароли не совпадают.";
    if (normalized.includes("user with this email") || normalized.includes("already exists")) return "Пользователь с таким email уже зарегистрирован.";
    return message;
  };

  const parseError = (value: unknown): string => {
    if (!value) return "Ошибка при регистрации.";
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

    if (!firstName || !lastName || !email || !password || !confirmPassword) {
      setError("Заполните все обязательные поля.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Пароли не совпадают.");
      return;
    }

    try {
      await register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone: phone || undefined,
      });
      navigate("/");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(parseError(err.response?.data?.detail ?? err.response?.data?.message));
      } else {
        setError("Ошибка при регистрации.");
      }
    }
  };

  return (
    <div className='auth'>
      <div className='auth__card'>
        <h2>Создайте аккаунт</h2>
        <p className='auth__subtitle'>Зарегистрируйтесь за пару секунд, чтобы заказывать пиццу быстрее.</p>
        <div className='auth__card__inputs'>
          <input
            type="text"
            className='username'
            placeholder='Имя'
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <input
            type="text"
            className='username'
            placeholder='Фамилия'
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
          <input
            type="text"
            className='username'
            placeholder='Телефон'
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
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
          <input
            type="password"
            className='password'
            placeholder='Повторите пароль'
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>
        {error && <p className='auth__error'>{error}</p>}
        <button className="signUp" type="button" onClick={handleSubmit}>
          Зарегистрироваться
        </button>
      </div>
    </div>
  );
};

export default CartSignUp;
