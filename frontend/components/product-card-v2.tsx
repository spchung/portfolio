"use client";
import { Product, Review } from "@/models";
import Image from "next/image";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@radix-ui/react-hover-card";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import ProductDetailDialog from "./product-detail-dialog";
import ProductReviewsDialog from "./product-review-dialog";

interface ProductCardProps extends React.ComponentPropsWithoutRef<"div"> {
  product: Product;
  reviews: Review[];
};

export function ProductCardV2({ product, reviews, className }: ProductCardProps) {
  const {
    title,
    images,
    description,
    store,
    main_category,
    categories,
  } = product;

  const primaryImage = images?.[0]?.large || images?.[0]?.thumb || "";

  return (
    <div className={cn("flex flex-row bg-gray-100 max-w-[800px] border rounded-lg shadow-sm overflow-hidden", className)}>
      <div className="w-1/5">
        <div className="h-28 relative flex flex-col">
          <Image
              src={primaryImage}
              alt={title}
              layout="fill"
              objectFit="cover"
              className="h-full w-full"
            />
        </div>
      </div>
      <div className="flex flex-col pl-2 w-3/5">
        <TitleHoverCard 
          title={title} 
          mainCategory={main_category} 
          categories={categories} 
          store={store} 
          className="text-m font-semibold p-0 h-7"
        />
        <p className="text-sm text-gray-700 line-clamp-3">
          {description || "No description provided."}
        </p>
      </div>
      <div className="w-1/5 pl-2">
        <div className="inline-flex flex-col items-center w-full max-w-xs">
          <ProductReviewsDialog product={product} reviews={reviews} className="w-full p-1 border border-gray-300 rounded-t-md text-center text-s"/>
          <ProductDetailDialog product={product} className="w-full p-1 border border-gray-300 rounded-t-md text-center text-s"/>
        </div>
      </div>
    </div>
  );
}

interface TitleHoverCardProps extends React.ComponentPropsWithoutRef<'h2'> {
  title: string;
  mainCategory: string;
  categories: string;
  store: string;
}

function TitleHoverCard({ 
    title, 
    className,
    mainCategory,
    categories,
    store,
  }: TitleHoverCardProps) {
  const trimmedTitle = title.slice(0, 30) + "...";
  
  return <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="link" className={cn(className, 'text-sm pl-0 justify-start')}>
          <p className="text-wrap text-start">{trimmedTitle}</p> 
        </Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-100">
        <div className="flex flex-col justify-between bg-gray-300 p-4 rounded-lg">
            <p className="text-sm text-black text-wrap max-w-[300px]">
              <span className="font-bold">Title: </span>
              {title}
            </p>
            <p className="text-sm text-black">
              <span className="font-bold">Category: </span>
              {mainCategory || categories}
            </p>
            <p className="text-sm text-black">
              {store && (
                <><span className="font-bold">Store:</span> {store} </>
              )}
            </p>
        </div>
      </HoverCardContent>
  </HoverCard>
}

