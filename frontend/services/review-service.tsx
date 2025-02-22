import { Review } from "@/models/index";
import { BatchResponse } from "@/models/index";

const fetchBatchReviews = async (reviewIds: string[]) => {
    const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/review/batch`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: reviewIds }),
        }
    )
    return await response.json() as BatchResponse<Review>;
}

const fetchReviewById = async (reviewId: string) => {
    const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/review/${reviewId}`
    )
    return await response.json() as Review;
}

const fetchProductReviews = async (productId: string) => {
    const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/review/product/${productId}`
    )
    return await response.json() as Review[];
}

export { fetchBatchReviews, fetchReviewById, fetchProductReviews };
