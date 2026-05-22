import React from "react";
import { useState, useContext } from "react";

type FilterState = {
  searchValue: string;
  categoryId: number;
  currentPage: number;
};

type FilterContextType = FilterState & {
  setCategoryId: (id: number) => void;
  setSearchValue: (v: string) => void;
  setCurrentPage: (p: number) => void;
  setFilters: (f: Partial<FilterState>) => void;
};

const defaultState: FilterState = {
  searchValue: "",
  categoryId: 0,
  currentPage: 1,
};

const FilterContext = React.createContext<FilterContextType | null>(null);

export const FilterProvider: React.FC<React.PropsWithChildren<{}>> = ({
  children,
}) => {
  const [state, setState] = useState<FilterState>(defaultState);

  const setCategoryId = (id: number) =>
    setState((s) => ({ ...s, categoryId: id }));
  const setSearchValue = (v: string) =>
    setState((s) => ({ ...s, searchValue: v }));
  const setCurrentPage = (p: number) =>
    setState((s) => ({ ...s, currentPage: p }));
  const setFilters = (f: Partial<FilterState>) =>
    setState((s) => ({ ...s, ...f }));

  const value: FilterContextType = {
    ...state,
    setCategoryId,
    setSearchValue,
    setCurrentPage,
    setFilters,
  };

  return (
    <FilterContext.Provider value={value}>{children}</FilterContext.Provider>
  );
};

export const useFilterContext = (): FilterContextType => {
  const ctx = useContext(FilterContext);
  if (!ctx)
    throw new Error("useFilterContext must be used within FilterProvider");
  return ctx;
};
