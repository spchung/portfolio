import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Product } from "@/models";
import { cn } from "@/lib/utils";
import Image from "next/image";

interface ProductCardProps extends React.ComponentPropsWithoutRef<"div"> {
    product: Product;
};

export default function ProductDetailDialog({ product, className }: ProductCardProps) {
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
        parent_asin,
    } = product;
    
    const primaryImage = images?.[0]?.large || images?.[0]?.thumb || "";

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="outline" className={cn(className)}>Details</Button>
            </DialogTrigger>
            <DialogContent className="max-w-[50%]">
                <DialogHeader>
                    <DialogTitle>Parent ASIN: {parent_asin}</DialogTitle>
                    <DialogDescription>
                        {title}
                    </DialogDescription>
                </DialogHeader>
                <div>
                    <div className="flex items-center mb-4">
                        {price !== null ? (
                            <p className="text-s font-bold text-primary-600">
                                ${price.toFixed(2)}
                            </p>
                            ) : (
                            <p className="text-s font-bold text-gray-400">Price Unavailable</p>
                        )}
                        <div className="flex items-center ml-4">
                            <StarRating rating={average_rating} />
                            <span className="ml-2 text-sm text-gray-600">
                                ({rating_number})
                            </span>
                        </div>
                    </div>
                    <div className="flex">
                        <div className="h-60 min-w-40 relative flex flex-col mr-2"> 
                            <Image
                                src={primaryImage}
                                alt={title}
                                layout="fill"
                                objectFit="cover"
                                className="h-full w-full"
                            />
                        </div>
                        <div className="overflow-y-auto">
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
                        </div>
                    </div>
                </div>
                {/* <DialogFooter>
                    <Button type="submit">Action</Button>
                </DialogFooter> */}
            </DialogContent>
        </Dialog>
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