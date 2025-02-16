"use client";
import { useState } from "react";
import { Product } from "@/models";
import { motion } from "framer-motion";

type ProductCardProps = {
  product: Product;
};

export function ProductCard({ product }: ProductCardProps) {
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

  // Pick which image to display as the primary image.
  // You could also implement a carousel or image gallery.
  const primaryImage = images?.[0]?.large || images?.[0]?.thumb || "";
  const thumbnailImage = images?.[0]?.thumb || images?.[0]?.large || "";

  return (
    <div className="flex flex-col md:flex-row max-w-3xl w-full border rounded-lg shadow-sm overflow-hidden">
      {/* Left Side: Product Image */}
      <div className="w-full md:w-1/5 h-48 relative bg-gray-100">
        {primaryImage ? (
          <img
            src={primaryImage}
            alt={title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            No image available
          </div>
        )}
      </div>

      {/* Right Side: Product Info */}
      <div className="flex flex-col p-4 w-full md:w-1/2">
        {/* Title */}
        <h2 className="text-xl font-semibold mb-1">{title}</h2>

        {/* Category & Store */}
        <p className="text-sm text-gray-500 mb-2">
          <span className="font-medium">Category: </span>
          {main_category || categories}
          {store && (
            <>
              {" "} | <span className="font-medium">Store:</span> {store}
            </>
          )}
        </p>

        {/* Price */}
        {price !== null ? (
          <p className="text-lg font-bold text-primary-600">
            ${price.toFixed(2)}
          </p>
        ) : (
          <p className="text-lg font-bold text-gray-400">Price Unavailable</p>
        )}

        {/* Rating */}
        <div className="flex items-center mt-2 mb-4">
          <StarRating rating={average_rating} />
          <span className="ml-2 text-sm text-gray-600">
            ({rating_number} ratings)
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-700 mb-4 line-clamp-3">
          {description || "No description provided."}
        </p>

        {/* Features (optional) */}
        <motion.div initial={{ height: 0 }} animate={{ height: seeMore ? "auto" : 0 }} className="overflow-hidden">
            {features && (
            <p className="text-sm text-gray-700 mb-4 italic">
                <span className="font-semibold">Features:</span> {features}
            </p>
            )}

            {/* Details (optional key-value info, if it's truly a Map) */}
            {details && (details as Map<string, string>).size > 0 && (
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
            )}
        </motion.div>
        <p className="text-blue-600 mt-0 cursor-pointer text-xs" onClick={() => setSeeMore(!seeMore)}>
          {seeMore ? "See Less" : "See More"}
        </p>

        {/* Action button (e.g., add to cart) */}
        <div className="mt-auto pt-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
            Action Btn
          </button>
        </div>
      </div>
    </div>
  );
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
