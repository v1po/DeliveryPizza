import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import { Categories, Sort, PizzaBlock, Skeleton, Pagination } from '../components';

import { useAppDispatch } from '../redux/store';
import { selectFilter } from '../redux/filter/selectors';
import { selectPizzaData } from '../redux/pizza/selectors';
import { setCategoryId, setCurrentPage } from '../redux/filter/slice';
import { fetchPizzas } from '../redux/pizza/asyncActions';

import TitlePage from '../components/Titles/TitlePage';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const isMounted = React.useRef(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);

  const { items, status } = useSelector(selectPizzaData);
  const { categoryId, sort, currentPage, searchValue } = useSelector(selectFilter);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');
    
    if (userData && token) {
      try {
        const parsedUser = JSON.parse(userData);
        setUserInfo(parsedUser);

        const registrationTime = localStorage.getItem('registration_time');
        
        if (registrationTime && 
            (Date.now() - parseInt(registrationTime)) < 10000 && 
            !hasShownWelcome &&
            parsedUser?.first_name) {
          
          setTimeout(() => {
            alert(`🎉 Добро пожаловать, ${parsedUser.first_name}!\n\nВаш аккаунт успешно создан. Приятных покупок!`);
            setHasShownWelcome(true);
          }, 500); 
          
          setTimeout(() => {
            localStorage.removeItem('registration_time');
          }, 10000);
        }
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }
  }, [hasShownWelcome]);

  const onChangeCategory = React.useCallback((idx: number) => {
    dispatch(setCategoryId(idx));
  }, []);

  const onChangePage = (page: number) => {
    dispatch(setCurrentPage(page));
  };

  const getPizzas = async () => {
    const sortBy = sort.sortProperty.replace('-', '');
    const order = sort.sortProperty.includes('-') ? 'asc' : 'desc';
    const category = categoryId > 0 ? String(categoryId) : '';
    const search = searchValue;

    dispatch(
      fetchPizzas({
        sortBy,
        order,
        category,
        search,
        currentPage: String(currentPage),
      }),
    );

    window.scrollTo(0, 0);
  };

  React.useEffect(() => {
    getPizzas();
  }, [categoryId, sort.sortProperty, searchValue, currentPage]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('registration_time');
    setUserInfo(null);
    setHasShownWelcome(false);
    navigate('/');
  };

  const pizzas = items.map((obj: any) => <PizzaBlock key={obj.id} {...obj} />);
  const skeletons = [...new Array(6)].map((_, index) => <Skeleton key={index} />);

  return (
    <div className="container">
      {userInfo && (
        <div className="user-info-panel">
          <div className="user-info-content">
            <div className="user-greeting">
              <span>👋 Привет, {userInfo.first_name}!</span>
              <span className="user-email">{userInfo.email}</span>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              Выйти
            </button>
          </div>
        </div>
      )}

      <TitlePage />
      <div className="content__top">
        <Categories value={categoryId} onChangeCategory={onChangeCategory} />
        <Sort value={sort} />
      </div>
      <h2 className="content__title">Все пиццы</h2>
      {status === 'error' ? (
        <div className="content__error-info">
          <h2>Произошла ошибка :(</h2>
          <p>Попробуйте повторить попытку позже.</p>
        </div>
      ) : (
        <div className="content__items">{status === 'loading' ? skeletons : pizzas}</div>
      )}

      <Pagination currentPage={currentPage} onChangePage={onChangePage} />
    </div>
  );
};

export default Home;