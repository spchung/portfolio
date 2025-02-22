"use client";
import { Product, Review } from "@/models";
import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { SkinCareIcon } from "./skincare-icon";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@radix-ui/react-hover-card";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import ProductDetailDialog from "./product-detail-dialog";
import ProductReviewsDialog from "./product-review-dialog";

interface ProductCardProps extends React.ComponentPropsWithoutRef<"div"> {
    product: Product;
    reviews: Review[] | undefined;
};

export function ProductCard({ product, reviews, className }: ProductCardProps) {
    const {
        brand_name,
        product_name,
        product_id,
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
                category={secondary_category} 
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
    category: string;
    store: string;
    reviews?: Review[];
}

function ProductOverview({ 
    title, 
    className,
    mainCategory,
    category,
    store,
    reviews,
    productId,
}: ProductOverviewProps) {
    const dialogRef = useRef<HTMLButtonElement>(null);
    const trimmedTitle = title.slice(0, 50);
    
    return (
        <>
            <div className={cn("flex flex-col justify-start w-full p-3", className)}>
                <div className="flex flex-row gap-3">
                    <div className="min-w-[30px] min-h-[30px]">
                        <SkinCareIcon type={category} width={35} height={35} />
                    </div>
                    <div className="flex flex-row justify-between w-[95%] items-center">
                        <p className="w-full font-bold overflow-hidden text-ellipsis truncate text-start">{trimmedTitle}</p>
                        {reviews ? (
                            <button 
                                className="min-w-10 text-gray-500 font-bold hover:text-gray-700 hover:underline"
                                onClick={() => dialogRef.current?.click()}
                            >
                                <MdReviews className="mt-1 h-6 w-6"/>
                            </button>
                        ) : null}
                    </div>
                </div>
                <div className="flex flex-row gap-[10px] mt-1">
                    <p className="text-sm text-gray-500">{category}</p>
                    <p className="text-sm text-gray-500">{store}</p>
                </div>
            </div>
            <ReviewsDialog 
                reviews={reviews ?? []} 
                productId={productId} 
                productCategory={category} 
                productName={title} 
                productBrand={store}
                ref={dialogRef}
            />
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
    productCategory: string;
    productName: string;
    productBrand: string;
    ref: React.RefObject<HTMLButtonElement | null>;
}

function ReviewsDialog({ reviews, productId, productCategory, productName, productBrand, ref }: ReviewsDialog) {
    const [isLoadOtherReviews, setIsLoadOtherReviews] = useState(false);

    const { isPending: reviewIsPending, error: reviewHasError, data: otherReviews, isFetching: reviewIsFetching } = useQuery({
        queryKey: ['productId', productId],
        queryFn: () => fetchProductReviews(productId).then((data) => {
            let existingRevewIds = reviews.map((review) => review.review_id);
            return data.filter((review) => !existingRevewIds.includes(review.review_id));
        }),
        enabled: isLoadOtherReviews,
      })

    return (
        <Dialog >
            <DialogTrigger asChild className="hidden">
                <Button ref={ref} variant="outline">Reviews</Button>
            </DialogTrigger>
            <DialogContent className="max-w-[60%] max-h-[80%] overflow-y-auto">
                <DialogHeader>
                    <div className="flex flex-row gap-4 items-center">
                        <SkinCareIcon type={productCategory} width={50} height={50} />
                        <DialogTitle className="text-[25px]"> {productName} </DialogTitle>
                        <p className="mt-auto">by <span className="font-bold">{productBrand}</span></p>
                    </div>
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
                                    { reviewIsPending ? 'Loading...' : reviewHasError ? 'An error has occurred: ' + reviewHasError.message : otherReviews.map((review) => (
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

import { FaRegThumbsDown } from "react-icons/fa";
import { FaRegThumbsUp } from "react-icons/fa";

function ReviewContainer(review: Review) {
    return (
        <div className={`flex flex-col justify-start w-full rounded-lg p-4 ${review.is_recommended ? 'bg-blue-100' : 'bg-orange-100'}`}>
            <div className="flex flex-row gap-2 w-full items-center">
                {review.is_recommended ? <FaRegThumbsUp className="h-4 w-4"/> : <FaRegThumbsDown className="h-4 w-4"/>}
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