import React from 'react';

import './SignUp.scss';

const CartSignUp: React.FC = () => {
  return(
    <div className='auth'>
      <div className='auth__card'>
        <h2>Регистрация</h2>
        <div className='auth__card__inputs'>
          <input type = "text" className='username' placeholder='Ваше имя'/>
          <input type = "text" className='username' placeholder='Номер телефона'/>
          <input type = "text" className='username' placeholder='Логин'/>
          <input type = "text" className='password' placeholder='Пароль'/>
          <input type = "text" className='password' placeholder='Повторите пароль'/>
        </div>
        <button className ="signUp">Зарегестрироваться</button>
      </div>
    </div>
  )
};

export default CartSignUp;
