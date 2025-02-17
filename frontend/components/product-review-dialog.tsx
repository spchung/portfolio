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
import { Product, Review } from "@/models";
import { cn } from "@/lib/utils";
import Image from "next/image";
import { Label} from "@/components/ui/label";

interface ProductReviewsDialog extends React.ComponentPropsWithoutRef<"div"> {
    product: Product;
    reviews: Review[];
};

export default function ProductDetailDialog({ product, reviews, className }: ProductReviewsDialog) {
    const {
        title,
        images,
        parent_asin,
    } = product;    
    
    const primaryProductImage = images?.[0]?.large || images?.[0]?.thumb || "";

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="outline" className={cn(className)}>Reviews ({reviews.length})</Button>
            </DialogTrigger>
            <DialogContent className="max-w-[50%]">
                <DialogHeader>
                    <DialogTitle>Parent ASIN: {parent_asin}</DialogTitle>
                    <DialogDescription>
                        {title}
                    </DialogDescription>
                    <DialogDescription>
                    </DialogDescription>
                </DialogHeader>

                {reviews.map((review) => (
                    <ReviewLabelText key={review.id} reviewTitle={review.title} reviewText={review.text} />
                ))}
            </DialogContent>
        </Dialog>
    )
}


function ReviewLabelText({ reviewTitle, reviewText }: { reviewTitle: string, reviewText: string }) {
    return (
        <div>
            <Label className="text-md font-bold"> {reviewTitle} </Label>
            <p className="text-gray-600">{reviewText}</p>
        </div>
    )
}