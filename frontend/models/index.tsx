export type ChatContext = {
    session_id:      string;
    history:         History[];
    metadata:        Metadata;
    running_summary: string;
    last_prompt:     string;
    product_ids:     string[];
    review_ids:      string[];
    named_entities:  NamedEntity[];
}

export type NamedEntity = {
    label: string;
    text: string;
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
}

export type Product = {
    brand_name:         string;
    product_name:       string;
    rating:             number;
    size:               string;
    price_usd:          number;
    highlights:         string[];
    teritary_category:  null;
    loves_count:        number;
    brand_id:           number;
    product_id:         string;
    reviews:            number;
    ingredients:        string[];
    primary_category:   string;
    secondary_category: string;
}

export type Review = {
    review_id:                string;
    total_neg_feedback_count: number;
    hair_color:               string;
    rating:                   number;
    total_pos_feedback_count: number;
    product_id:               string;
    author_id:                string;
    submission_time:          Date;
    product_name:             string;
    review_text:              string;
    brand_name:               string;
    is_recommended:           boolean;
    review_title:             string;
    price_usd:                number;
    skin_tone:                string;
    helpfulness:              number;
    eye_color:                string;
    total_feedback_count:     number;
    skin_type:                string;
}


export type BatchResponse<T> = {
    data: T[];
    meta_data: {
        total: number;
    }
}
