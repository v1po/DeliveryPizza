import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { addItem } from '../../redux/cart/slice';
import { selectCartItemById } from '../../redux/cart/selectors';
import { CartItem } from '../../redux/cart/types';
import axios from 'axios';

const typeNames = ['тонкое', 'традиционное'];

const FullPizza: React.FC = () => {
  const [pizza, setPizza] = useState<{
    id: string;
    imageUrl: string;
    title: string;
    price: number;
    sizes: number[];
    types: number[];
  } | null>(null);
  
  const [activeType, setActiveType] = useState(0);
  const [activeSize, setActiveSize] = useState(0);
  
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const cartItem = useSelector(selectCartItemById(id || ''));
  const addedCount = cartItem ? cartItem.count : 0;

  useEffect(() => {
    async function fetchPizza() {
      try {
        const { data } = await axios.get(`https://690a6a8d1a446bb9cc2283e3.mockapi.io/items?id=${id}`);
        setPizza(data);
      } catch (error) {
        console.error('Ошибка при получении пиццы:', error);
        alert('Ошибка при получении пиццы!');
        navigate('/');
      }
    }

    if (id) {
      fetchPizza();
    }
  }, [id, navigate]);

  const onClickAdd = () => {
    if (!pizza) return;
    
    const item: CartItem = {
      id: pizza.id,
      title: pizza.title,
      price: pizza.price,
      imageUrl: pizza.imageUrl,
      type: typeNames[activeType],
      size: pizza.sizes?.[activeSize] || 26,
      count: 0,
    };
    
    dispatch(addItem(item));
  };

  if (!pizza) {
    return (
      <div className="container">
        <div className="pizza-skeleton">
          <div className="skeleton-image"></div>
          <div className="skeleton-title"></div>
          <div className="skeleton-price"></div>
          <div className="skeleton-buttons"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="full-pizza">
        <img 
          className="full-pizza__image" 
          src={pizza.imageUrl} 
          alt={pizza.title} 
        />
        
        <div className="full-pizza__info">
          <h2 className="full-pizza__title">{pizza.title}</h2>
          {pizza.types && pizza.types.length > 0 && (
            <div className="full-pizza__selector">
              <h4>Выберите тесто:</h4>
              <ul>
                {pizza.types.map((typeId) => (
                  <li
                    key={typeId}
                    onClick={() => setActiveType(typeId)}
                    className={activeType === typeId ? 'active' : ''}
                  >
                    {typeNames[typeId]}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {pizza.sizes && pizza.sizes.length > 0 && (
            <div className="full-pizza__selector">
              <h4>Выберите размер:</h4>
              <ul>
                {pizza.sizes.map((size, index) => (
                  <li
                    key={size}
                    onClick={() => setActiveSize(index)}
                    className={activeSize === index ? 'active' : ''}
                  >
                    {size} см.
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="full-pizza__price">
            Цена: <strong>{pizza.price} ₽</strong>
          </div>
          
          <div className="full-pizza__actions">
            <button 
              className="button button--outline button--add" 
              onClick={onClickAdd}
            >
              <svg
                width="12"
                height="12"
                viewBox="0 0 12 12"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10.8 4.8H7.2V1.2C7.2 0.5373 6.6627 0 6 0C5.3373 0 4.8 0.5373 4.8 1.2V4.8H1.2C0.5373 4.8 0 5.3373 0 6C0 6.6627 0.5373 7.2 1.2 7.2H4.8V10.8C4.8 11.4627 5.3373 12 6 12C6.6627 12 7.2 11.4627 7.2 10.8V7.2H10.8C11.4627 7.2 12 6.6627 12 6C12 5.3373 11.4627 4.8 10.8 4.8Z"
                  fill="white"
                />
              </svg>
              <span>Добавить</span>
              {addedCount > 0 && <i>{addedCount}</i>}
            </button>
            
            <Link to="/">
              <button className="button button--outline button--back">
                <span>← Назад</span>
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FullPizza;