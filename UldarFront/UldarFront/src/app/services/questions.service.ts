import { Injectable } from '@angular/core';
import { QuestionDetailResponse, Questions } from '../models';
import { Observable, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { JwtHelperService } from "@auth0/angular-jwt";
import { Router } from "@angular/router";

let helper = new JwtHelperService()

@Injectable({
  providedIn: 'root',
})
export class QuestionsService {
  //private apiURL = 'http://localhost:5000/questions';
  private base_url='http://127.0.0.1:8000/api/questions';

  constructor(private http: HttpClient, private router: Router) {
  }

  getQuestions(): Observable<Questions[]> {
    return this.http.get<Questions[]>(`${this.base_url}/list`);
  }

  getQuestion(slug: string): Observable<QuestionDetailResponse> {
    return this.http.get<QuestionDetailResponse>(`${this.base_url}/${slug}/retrieve`);
  }

  deleteQuestion(slug: string): Observable<any> {
    return this.http.delete(`${this.base_url}/${slug}/delete`);
  }

  updateQuestion(question: Questions): Observable<Questions> {
    return this.http.put<Questions>(`${this.base_url}/${question.slug}/update`, question);
  }

  addQuestion(question: Questions): Observable<Questions> {
    return this.http.post<Questions>(`${this.base_url}/create`, question);
  }
}
