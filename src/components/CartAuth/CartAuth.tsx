import React from 'react';
import { Link, useLocation } from 'react-router-dom';

import './auth.scss';

const CartAuth: React.FC = () => {
  return(
    <div className='auth'>
      <div className='auth__card'>
        <h2>Авторизация</h2>
        <div className='auth__card__inputs'>
          <input type = "text" className='username' placeholder='Логин'/>
          <input type = "text" className='password' placeholder='Пароль'/>
        </div>
        <button className ="logIn">Войти</button>
        <Link to='/signup'>
                <button className='signUp' >Зарегестрироваться</button></Link>
      </div>
    </div>
  )
};

export default CartAuth;
