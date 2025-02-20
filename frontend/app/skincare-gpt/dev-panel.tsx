import { useEffect } from 'react';
import { useRagStore } from '@/stores/use-rag-store';
import { useContext } from '@/hooks/use-context';
// import { ProductCard } from '@/components/product-card';
import { ProductCardV2 } from '@/components/product-card-v2';
import { Review } from '@/models';


export default function DevPanel() {
  const { context } = useContext();

  const history = context?.history;
  const runningSummary = context?.running_summary;
  const last_prompt = context?.last_prompt;
  const intent = context?.metadata.last_query_intent;
  const products = context?.metadata.products;
  const reviews = context?.metadata.reviews;

  useEffect(() => {
    console.log(last_prompt);
  }, [last_prompt]);

  return (
    <div className='flex flex-col h-full'>
      <div className='flex-1'>
        {
          products?.map((product) => (
            <ProductCardV2 
              key={product.id} 
              product={product} 
              reviews={findProductReviews(product.parent_asin, reviews) ?? []}
              className="p-2 mb-1"
            />
          ))
        }
      </div>
      <div className='flex-1'> 
        <h2>Summary</h2>
        <p>{runningSummary}</p>
        <h2>Intent: {intent}</h2>
      </div>
    </div>
  )
}


function findProductReviews(productParentASIN: string, reviews: Review[] | undefined): Review[] | undefined {
  if (!reviews) return undefined;
  return reviews.filter(review => review.parent_asin === productParentASIN);
}