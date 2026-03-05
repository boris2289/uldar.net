export interface AuthToken{
    refresh:string;
    access:string;
}
export interface Comments {
    id: number;
    text: string;
    author: number;
    question: number;
}
export interface Questions {
    id: number;
    title: string;
    description: string;
    author: number;
    slug: string;
    tag: number[];
    created_at: Date;
    updated_at: Date;
    is_active: boolean;
}
export interface Tags {
    id: number;
    name: string;
    slug: string;
}
export interface Users {
    id: number,
    first_name: string,
    second_name: string,
    email: string,
  }

export interface TagDetailResponse {
  tag: Tags;
  questions: Questions[];
}

export interface QuestionDetailResponse {
    question : Questions,
    comments : Comments[],
    tags : Tags[]
}
