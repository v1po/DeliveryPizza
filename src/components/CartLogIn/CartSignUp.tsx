import React, { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import "./SignUp.scss";
import { FiMail, FiLock, FiUser, FiPhone, FiCheck } from "react-icons/fi";
import { useNavigate } from "react-router-dom";

interface FormData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone: string;
}

const CartSignUp: React.FC = () => {
  const navigate = useNavigate();
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [userData, setUserData] = useState<any>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<FormData>();

  const password = watch("password", "");

  const validatePassword = (value: string) => {
    if (!/[A-Z]/.test(value)) return "Должна быть хотя бы одна заглавная буква";
    if (!/[a-z]/.test(value)) return "Должна быть хотя бы одна строчная буква";
    if (!/\d/.test(value)) return "Должна быть хотя бы одна цифра";
    if (value.length < 8) return "Минимум 8 символов";
    return true;
  };

  const onSubmit = async (data: FormData) => {
    try {
      const requestBody = {
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone || undefined,
      };
      const registerResponse = await axios.post(
        "http://localhost:8001/api/v1/auth/register",
        requestBody,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (registerResponse.status === 201 || registerResponse.status === 200) {
        try {
          const loginResponse = await axios.post(
            "http://localhost:8001/api/v1/auth/login",
            {
              email: data.email,
              password: data.password,
            },
            {
              headers: {
                "Content-Type": "application/json",
              },
            }
          );

          if (loginResponse.data?.data) {
            const { access_token, refresh_token, user } =
              loginResponse.data.data;

            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", refresh_token);

            if (user) {
              localStorage.setItem("user", JSON.stringify(user));
              setUserData(user);
            }

            localStorage.setItem("registration_time", Date.now().toString());

            setRegistrationSuccess(true);

            setTimeout(() => {
              navigate("/");
            }, 3000);
          }
        } catch (loginError: any) {
          setRegistrationSuccess(true);
          setUserData({
            first_name: data.first_name,
            email: data.email,
          });

          localStorage.setItem("registration_time", Date.now().toString());

          setTimeout(() => {
            navigate("/auth");
          }, 3000);
        }
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "Ошибка регистрации";
      alert(`Ошибка: ${errorMessage}`);
    }
  };

  if (registrationSuccess) {
    return (
      <div className="auth">
        <div className="auth__container">
          <div className="auth__right">
            <div className="auth__card auth__success">
              <div className="success-icon">
                <FiCheck size={64} />
              </div>
              <h2>Регистрация успешна!</h2>
              <p className="auth__card__subtitle">
                Добро пожаловать, {userData?.first_name || "Пользователь"}!
              </p>
              <p>
                Вы будете перенаправлены на главную страницу через 3 секунды...
              </p>
              <button
                onClick={() => navigate("/")}
                className="signUp"
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
            <h2>Регистрация</h2>
            <p className="auth__card__subtitle">Создайте аккаунт для заказов</p>

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
                      validate: validatePassword,
                    })}
                  />
                  {errors.password && (
                    <span className="error-message">
                      {errors.password.message}
                    </span>
                  )}
                </div>

                <div className="auth__input-group">
                  <FiUser className="auth__input-icon" />
                  <input
                    type="text"
                    placeholder="Имя"
                    {...register("first_name", {
                      required: "Имя обязательно",
                      minLength: {
                        value: 1,
                        message: "Имя слишком короткое",
                      },
                      maxLength: {
                        value: 100,
                        message: "Имя слишком длинное",
                      },
                    })}
                  />
                  {errors.first_name && (
                    <span className="error-message">
                      {errors.first_name.message}
                    </span>
                  )}
                </div>

                <div className="auth__input-group">
                  <FiUser className="auth__input-icon" />
                  <input
                    type="text"
                    placeholder="Фамилия"
                    {...register("last_name", {
                      required: "Фамилия обязательна",
                      minLength: {
                        value: 1,
                        message: "Фамилия слишком короткая",
                      },
                      maxLength: {
                        value: 100,
                        message: "Фамилия слишком длинная",
                      },
                    })}
                  />
                  {errors.last_name && (
                    <span className="error-message">
                      {errors.last_name.message}
                    </span>
                  )}
                </div>

                <div className="auth__input-group">
                  <FiPhone className="auth__input-icon" />
                  <input
                    type="tel"
                    placeholder="Номер телефона"
                    {...register("phone", {
                      maxLength: {
                        value: 20,
                        message: "Телефон слишком длинный",
                      },
                    })}
                  />
                  {errors.phone && (
                    <span className="error-message">
                      {errors.phone.message}
                    </span>
                  )}
                </div>
              </div>

              <div className="password-requirements">
                <h4>Требования к паролю:</h4>
                <ul>
                  <li className={password.length >= 8 ? "valid" : ""}>
                    Минимум 8 символов
                  </li>
                  <li className={/[A-Z]/.test(password) ? "valid" : ""}>
                    Хотя бы одна заглавная буква
                  </li>
                  <li className={/[a-z]/.test(password) ? "valid" : ""}>
                    Хотя бы одна строчная буква
                  </li>
                  <li className={/\d/.test(password) ? "valid" : ""}>
                    Хотя бы одна цифра
                  </li>
                </ul>
              </div>

              <button type="submit" className="signUp" disabled={isSubmitting}>
                {isSubmitting ? "Регистрация..." : "Зарегистрироваться"}
              </button>
            </form>

            <div className="auth__footer">
              <p>
                Уже есть аккаунт? <a href="/auth">Войти</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartSignUp;
