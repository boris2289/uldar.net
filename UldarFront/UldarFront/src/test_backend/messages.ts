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
