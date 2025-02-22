"use client";
import { Product, Review } from "@/models";
import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@radix-ui/react-hover-card";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import ProductDetailDialog from "./product-detail-dialog";
import ProductReviewsDialog from "./product-review-dialog";

interface ProductCardProps extends React.ComponentPropsWithoutRef<"div"> {
    product: Product;
    reviews: Review[] | undefined;
};

export function ProductCardV2({ product, reviews, className }: ProductCardProps) {
    const {
        brand_name,
        product_name,
        rating,
        size,
        price_usd,
        highlights,
        teritary_category,
        loves_count,
        brand_id,
        product_id,
        reviews: reveiwCount,
        ingredients,
        primary_category,
        secondary_category,
    } = product;

    const [productReviewMap, setProductReviewMap] = useState(new Map<string, Review[]>(null));

    useEffect(() => {
        if (reviews) {
            const productReviewMap = new Map<string, Review[]>();
            reviews.forEach((review) => {
                if (productReviewMap.has(review.product_id)) {
                    productReviewMap.get(review.product_id)?.push(review);
                } else {
                    productReviewMap.set(review.product_id, [review]);
                }
            });
            setProductReviewMap(productReviewMap);
        }
    }, [reviews]);

    return (
        <div className={cn("flex flex-row bg-gray-100 border rounded-lg shadow-sm overflow-hidden text-ellipsis", className)}>
            <ProductOverview 
                productId={product_id}
                title={product_name} 
                mainCategory={primary_category} 
                categories={secondary_category} 
                store={brand_name} 
                className="text-m font-semibold"
                {...(productReviewMap ? { reviews: productReviewMap.get(product_id) } : {})}
            />
        </div>
    );
}

import { MdReviews } from "react-icons/md";

interface ProductOverviewProps extends React.ComponentPropsWithoutRef<'h2'> {
    productId: string;
    title: string;
    mainCategory: string;
    categories: string;
    store: string;
    reviews?: Review[];
}

function ProductOverview({ 
    title, 
    className,
    mainCategory,
    categories,
    store,
    reviews,
    productId,
}: ProductOverviewProps) {
    const dialogRef = useRef<HTMLButtonElement>(null);
    const trimmedTitle = title.slice(0, 50);
    
    return (
        <>
            <div className={cn("flex flex-col justify-start w-full p-3", className)}>
                <div className="flex flex-row justify-between w-full">
                    <p className="w-[95%] font-bold overflow-hidden text-ellipsis truncate">{trimmedTitle}</p>
                    {
                        reviews ? (
                            <button 
                                className="w-10 text-gray-500 pt-1 font-bold flex hover:text-gray-700 flex-row gap-[3px] hover:underline"
                                onClick={() => dialogRef.current?.click()}
                            >
                                <MdReviews className="mt-1 h-6 w-6"/>
                            </button>
                        ) : null
                    }
                </div>
                <div className="flex flex-row gap-[10px]">
                    <p className="text-sm text-gray-500">{mainCategory}</p>
                    <p className="text-sm text-gray-500">{categories}</p>
                    <p className="text-sm text-gray-500">{store}</p>
                </div>
                {reviews ? (
                    <div className="flex flex-row gap-[10px]">
                        <p className="text-sm text-gray-500">{reviews.length} reviews</p>
                        <p className="text-sm text-gray-500">{reviews.reduce((acc, review) => acc + review.rating, 0) / reviews.length} stars</p>
                    </div>
                ) : <p className="text-sm text-gray-500"> No reviews </p>}
            </div>
            <ReviewsDialog reviews={reviews ?? []} productId={productId} productName={title} ref={dialogRef}/>
        </>
    )
}

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from "@tanstack/react-query";
import { fetchProductReviews } from '@/services/review-service';

interface ReviewsDialog {
    reviews: Review[];
    productId: string;
    productName: string;
    ref: React.RefObject<HTMLButtonElement | null>;
}

function ReviewsDialog({ reviews, productId, productName, ref }: ReviewsDialog) {

    const [otherReviews, setOtherReviews] = useState([]);
    const [isLoadOtherReviews, setIsLoadOtherReviews] = useState(false);

    const { isPending: reviewIsPending, error: reviewHasError, data: reviewData, isFetching: reviewIsFetching } = useQuery({
        queryKey: ['productId', productId],
        queryFn: () => fetchProductReviews(productId),
        enabled: isLoadOtherReviews,
      })

    return (
        <Dialog >
            <DialogTrigger asChild className="hidden">
                <Button ref={ref} variant="outline">Reviews</Button>
            </DialogTrigger>
            <DialogContent className="max-w-[80%] max-h-[80%] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle> {productName} </DialogTitle>
                    <div className="font-bold">Relavant Reviews:</div>
                    <div className="flex flex-col gap-2 pl-2">
                        {reviews.map((review) => (
                            <ReviewContainer {...review} key={review.review_id}/>
                        ))}
                    </div>
                    <AnimatePresence>
                        {isLoadOtherReviews && (
                            <motion.div
                                key="other-reviews"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                            >
                                <div className="font-bold"> Other Reviews: </div>
                                <div className="flex flex-col gap-2 pl-2">
                                    { reviewIsPending ? 'Loading...' : reviewHasError ? 'An error has occurred: ' + reviewHasError.message : reviewData.map((review) => (
                                        <ReviewContainer {...review} key={review.review_id}/>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                    </AnimatePresence>
                    <div>
                        <button 
                            className='pt-2 hover:underline text-gray-500'
                            onClick={() => setIsLoadOtherReviews(!isLoadOtherReviews)}
                        > {isLoadOtherReviews ? "Hide other reviews" : "See other reviews..."} </button>
                    </div>
                </DialogHeader>
            </DialogContent>
        </Dialog>
    )
}

function ReviewContainer(review: Review) {
    return (
        <div className="flex flex-col justify-start w-full">
            <div className="flex flex-row gap-2 w-full">
                <StarRating rating={review.rating} />
                <p className="font-bold text-lg overflow-hidden text-ellipsis truncate text-black">{review.review_title}</p>
            </div>
            <p className="text-sm text-gray-500">{review.review_text}</p>
        </div>
    )
}
function StarRating({ rating }: { rating: number }) {
    // Convert rating number into a 5-star visual
    const stars = Array.from({ length: 5 }, (_, i) => i < Math.round(rating));
    return (
      <div className="flex items-center">
        {stars.map((filled, i) => (
          <svg
            key={i}
            className={`h-4 w-4 ${
              filled ? "text-yellow-500" : "text-gray-300"
            }`}
            fill={filled ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth="1"
            viewBox="0 0 24 24"
          >
            <path d="M12 .587l3.668 7.568 8.332 1.2-6.001 5.85 1.416 8.263L12 18.771l-7.415 3.898 1.416-8.263-6.001-5.85 8.332-1.2z" />
          </svg>
        ))}
      </div>
    );
  }