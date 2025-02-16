
export type Context = {
    session_id:  string;
    history:     History[];
    window_size: number;
    metadata:    Metadata;
}

export type History = {
    user_query:  string;
    response:    string;
    user_intent: string;
    topic:       null;
    timestamp:   number;
    struct_data: null;
}

export type Metadata = {
    last_response_tokens:  number;
    last_query_start_time: number;
    last_query_end_time:   number;
    elapsed_seconds:       number;
    last_query_intent:     string;
    products:              Product[];
    reviews:               Review[];
}

export type Product = {
    parent_asin:    string;
    main_category:  string;
    id:             number;
    average_rating: number;
    store:          string;
    features:       string;
    price:          number | null;
    details:        Map<string, string>;
    meta:           null;
    title:          string;
    rating_number:  number;
    description:    string;
    images:         ProductImage[];
    categories:     string;
}

export type ProductImage = {
    thumb:   string;
    large:   string;
    variant: string;
    hi_res:  null | string;
}

export type Review = {
    asin:        string;
    title:       string;
    text:        string;
    parent_asin: string;
    timestamp:   string;
    images:      ReviewImage[];
    id:          number;
    user_id:     string;
}

export type ReviewImage = {
    small_image_url:  string;
    medium_image_url: string;
    large_image_url:  string;
    attachment_type:  string;
}