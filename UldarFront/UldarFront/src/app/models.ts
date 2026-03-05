export interface AuthToken{
    refresh:string;
    access:string;
}
export interface Messages {
    id: number;
    body: string;
    user: number;
    score: number;
    question: number;
    created: Date;
    updated: Date;
    is_best_answer: boolean;
    code_field: string;
}
export interface Questions {
    id: number;
    title: string;
    body: string;
    user: number;
    slug: string;
    tag: number;
    created: Date;
    updated: Date;
    is_active: boolean;
    code_field: string;
}
export interface Tags {
    id: number;
    name: string;
    description: string;
}
export interface Users {
    id: number,
    first_name: string,
    second_name: string,
    email: string,
  }
