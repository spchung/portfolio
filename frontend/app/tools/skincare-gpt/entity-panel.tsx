'use client';
import { ProductCard } from '@/components/product-card';
import { fetchBatchProducts } from '@/services/product-service';
import { fetchBatchReviews } from '@/services/review-service';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton"

const queryClient = new QueryClient();

interface EntityPanelProps extends React.ComponentPropsWithoutRef<"div"> {
    productIds: string[] | undefined;
    reviewIds: string[] | undefined;
}

/* Render reviews or products or both */
function EntityList({ productIds, reviewIds}: EntityPanelProps) {
    const { isPending: productIsPending, error: productHasError, data: productData, isFetching } = useQuery({
        queryKey: ['productIds', productIds],
        queryFn: () => fetchBatchProducts(productIds || []),
        enabled: !!productIds,
      })
    
    const { isPending: reviewIsPending, error: reviewHasError, data: reviewData, isFetching: reviewIsFetching } = useQuery({
        queryKey: ['reviedIds', reviewIds],
        queryFn: () => fetchBatchReviews(reviewIds || []),
        enabled: !!reviewIds,
      })
    
    if (productIsPending) return (
        <div className='flex flex-col'>
            <Skeleton className='h-20' />
            <Skeleton className='h-20' />
            <Skeleton className='h-20' />
        </div>
    )

    if (productHasError) return 'An error has occurred: ' + productHasError.message

    return (
        <div className='flex flex-col'>
            {productData.data.map((product) => (
                <div className='mb-1' key={product.product_id}>
                    <ProductCard product={product} reviews={reviewData?.data}/>
                </div>
            ))}
        </div>
    );
}


function EntityPanel({ productIds, reviewIds }: EntityPanelProps) {
    return (
        <QueryClientProvider client={queryClient}>
            <EntityList productIds={productIds} reviewIds={reviewIds} />
        </QueryClientProvider>
    );
}

export { EntityPanel };