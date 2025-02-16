import { useEffect } from 'react';
import { useRagStore } from '@/stores/use-rag-store';
import { useContext } from '@/hooks/use-context';
import { ProductCard } from '@/components/product-card';


export default function DevPanel() {
  const iterateContextCount = useRagStore(store => store.state.iterateContextCount);
  const { context } = useContext();

  const history = context?.history;
  const products = context?.metadata.products;
  const reviews = context?.metadata.reviews;

  return (
    <div className='flex flex-col h-full'>
      <div className='flex-1'>
        {
          products?.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))
        }
      </div>
      <div className='flex-1'> 
        Contexual information
      </div>
    </div>
  )
}
