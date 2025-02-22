import { Product } from "@/models/index";
import { BatchResponse } from "@/models/index";

const fetchBatchProducts = async (productIds: string[]) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v2/product/batch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ids: productIds }),
      }
    )
    return await response.json() as BatchResponse<Product>;
  };

const fetchProductById = async (productId: string) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v2/product/${productId}`
    )
    return await response.json() as Product;
  }

export { fetchBatchProducts, fetchProductById };