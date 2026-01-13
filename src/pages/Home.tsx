import axios from "axios";
import { useEffect, useState, useRef, useCallback } from "react";

import { Categories, PizzaBlock, Skeleton, Pagination } from "../components";
import TitlePage from "../components/Titles/TitlePage";
import { useFilterContext } from "../hooks/useFilterContext";

const Home = () => {
  const {
    categoryId,
    currentPage,
    searchValue,
    setCategoryId,
    setCurrentPage,
  } = useFilterContext();

  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );

  const onChangeCategory = useCallback(
    (idx: number) => {
      setCategoryId(idx);
    },
    [setCategoryId]
  );

  const onChangePage = (page: number) => {
    setCurrentPage(page);
  };

  const getPizzas = async () => {
    try {
      setStatus("loading");
      const category = categoryId > 0 ? String(categoryId) : "";
      const search = searchValue;

      const { data } = await axios.get(
        `https://690a6a8d1a446bb9cc2283e3.mockapi.io/items`,
        {
          params: {
            page: currentPage,
            limit: 4,
            category,
            search,
          },
        }
      );

      setItems(data);
      setStatus("success");
    } catch (e) {
      setStatus("error");
      setItems([]);
    }

    window.scrollTo(0, 0);
  };

  useEffect(() => {
    getPizzas();
  }, [categoryId, searchValue, currentPage]);

  const pizzas = items.map((obj: any) => <PizzaBlock key={obj.id} {...obj} />);
  const skeletons = [...new Array(6)].map((_, index) => (
    <Skeleton key={index} />
  ));

  return (
    <div className="container">
      <TitlePage />
      <div className="content__top">
        <Categories value={categoryId} onChangeCategory={onChangeCategory} />
      </div>
      <h2 className="content__title">Все пиццы</h2>
      {status === "error" ? (
        <div className="content__error-info">
          <h2>Произошла ошибка :(</h2>
          <p>Попробуйте повторить попытку позже.</p>
        </div>
      ) : (
        <div className="content__items">
          {status === "loading" ? skeletons : pizzas}
        </div>
      )}

      <Pagination currentPage={currentPage} onChangePage={onChangePage} />
    </div>
  );
};

export default Home;
