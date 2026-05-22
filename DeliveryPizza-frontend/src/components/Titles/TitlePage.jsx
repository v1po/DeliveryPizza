import { useEffect } from 'react';

function TitlePage() {
  useEffect(() => {
    document.title = 'Быстрая и удобная доставка продуктов';
  }, []);
  return (
    <></>
  );
}

export default TitlePage;
