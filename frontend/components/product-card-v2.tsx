"use client";
import React, { useState } from "react";
import { Product } from "@/models";
import { motion } from "framer-motion";
import Image from "next/image";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@radix-ui/react-hover-card";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

interface ProductCardProps extends React.ComponentPropsWithoutRef<"div"> {
  product: Product;
};

export function ProductCardV2({ product, className }: ProductCardProps) {
  const {
    title,
    price,
    average_rating,
    rating_number,
    images,
    description,
    store,
    main_category,
    categories,
    features,
    details,
  } = product;

  const [seeMore, setSeeMore] = useState(false);

  const primaryImage = images?.[0]?.large || images?.[0]?.thumb || "";
  const thumbnailImage = images?.[0]?.thumb || images?.[0]?.large || "";

  return (
    <div className={cn("flex flex-row bg-gray-100 max-w-[800px] border rounded-lg shadow-sm overflow-hidden", className)}>
      <div className="w-1/5">
        <div className="h-28 relative  flex flex-col">
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

        {/* Price */}
        {/* {price !== null ? (
          <p className="text-s font-bold text-primary-600">
            ${price.toFixed(2)}
          </p>
        ) : (
          <p className="text-s font-bold text-gray-400">Price Unavailable</p>
        )} */}
        <div className="flex items-center">
            <StarRating rating={average_rating} />
            <span className="ml-2 text-sm text-gray-600">
              ({rating_number})
            </span>
        </div>


        {/* Description */}
        <p className="text-sm text-gray-700 line-clamp-3">
          {description || "No description provided."}
        </p>

        {/* Features (optional) */}
        {/* <motion.div initial={{ height: 0 }} animate={{ height: seeMore ? "auto" : 0 }} className="overflow-hidden"> */}
            {/* {features && (
              <p className="text-sm text-gray-700 mb-4 italic">
                  <span className="font-semibold">Features:</span> {features}
              </p>
            )} */}

            {/* Details (optional key-value info, if it's truly a Map) */}
            {/* {details && (details as Map<string, string>).size > 0 && (
              <div className="mt-2">
                  <h3 className="text-sm font-semibold mb-1">Additional Details</h3>
                  <ul className="list-disc list-inside text-sm text-gray-700">
                  {Array.from((details as Map<string, string>).entries()).map(([key, value]) => (
                  <li key={key}>
                  <strong>{key}:</strong> {value}
                  </li>
                  ))}
                  </ul>
              </div>
            )} */}
        {/* </motion.div> */}
        {/* <p className="text-blue-600 mt-0 cursor-pointer text-xs" onClick={() => setSeeMore(!seeMore)}>
          {seeMore ? "See Less" : "See More"}
        </p> */}

        {/* Action button (e.g., add to cart) */}
      </div>
      <div className="w-1/5">
        <div className="inline-flex flex-col items-center w-full max-w-xs">
          {/* <!-- Top Button: Rounded top corners --> */}
          <button className="w-full p-1 border border-gray-300 rounded-t-md text-center">
            Action
          </button>
          
          {/* <!-- Bottom Button: Rounded bottom corners --> */}
          <button className="w-full p-1 border border-gray-300 rounded-b-md text-center">
            Read more
          </button>
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
        <Button variant="link" className={cn(className, 'pl-0 justify-start')}>{trimmedTitle}</Button>
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

// Optional small star rating component (Tailwind)
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
