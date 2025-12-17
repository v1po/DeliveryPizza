import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { FiMail, FiLock, FiCheck } from "react-icons/fi";
import axios from "axios";
import "./auth.scss";

interface LoginFormData {
  email: string;
  password: string;
}

const CartAuth: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const [userData, setUserData] = useState<any>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        "http://localhost:8001/api/v1/auth/login",
        {
          email: data.email,
          password: data.password,
        }
      );

      if (response.data.data?.access_token) {
        const { access_token, refresh_token, user } = response.data.data;

        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);

        if (user) {
          localStorage.setItem("user", JSON.stringify(user));
          setUserData(user);
        } else {
          const minimalUser = {
            email: data.email,
            first_name: data.email.split("@")[0],
          };
          localStorage.setItem("user", JSON.stringify(minimalUser));
          setUserData(minimalUser);
        }

        setLoginSuccess(true);

        setTimeout(() => {
          navigate("/");
        }, 3000);
      } else {
        throw new Error("Токен не получен");
      }
    } catch (err: any) {
      if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Ошибка соединения с сервером");
      }
    } finally {
      setLoading(false);
    }
  };

  // Если успешная авторизация
  if (loginSuccess) {
    return (
      <div className="auth">
        <div className="auth__container">
          <div className="auth__right">
            <div className="auth__card auth__success">
              <div className="success-icon">
                <FiCheck size={64} />
              </div>
              <h2>Авторизация успешна!</h2>
              <p className="auth__card__subtitle">
                Добро пожаловать,{" "}
                {userData?.first_name ||
                  userData?.email?.split("@")[0] ||
                  "Пользователь"}
                !
              </p>
              <p>
                Вы будете перенаправлены на главную страницу через 3 секунды...
              </p>
              <button
                onClick={() => navigate("/")}
                className="logIn"
                style={{ marginTop: "20px" }}
              >
                Перейти на главную сейчас
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth">
      <div className="auth__container">
        <div className="auth__right">
          <div className="auth__card">
            <h2>Авторизация</h2>
            <p className="auth__card__subtitle">Войдите в свой аккаунт</p>

            {error && <div className="auth__error">⚠️ {error}</div>}

            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="auth__card__inputs">
                <div className="auth__input-group">
                  <FiMail className="auth__input-icon" />
                  <input
                    type="email"
                    placeholder="Email"
                    {...register("email", {
                      required: "Email обязателен",
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: "Некорректный email",
                      },
                    })}
                  />
                  {errors.email && (
                    <span className="error-message">
                      {errors.email.message}
                    </span>
                  )}
                </div>

                <div className="auth__input-group">
                  <FiLock className="auth__input-icon" />
                  <input
                    type="password"
                    placeholder="Пароль"
                    {...register("password", {
                      required: "Пароль обязателен",
                    })}
                  />
                  {errors.password && (
                    <span className="error-message">
                      {errors.password.message}
                    </span>
                  )}
                </div>
              </div>

              <button type="submit" className="logIn" disabled={loading}>
                {loading ? "Вход..." : "Войти"}
              </button>
            </form>

            <div className="auth__footer">
              <p>
                Нет аккаунта? <Link to="/signup">Зарегистрироваться</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartAuth;