import { Injectable } from '@angular/core';
import { Questions, question_list } from '../../test_backend/questions';
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
  private base_url='http://localhost:8000/api/questions';

  constructor(private http: HttpClient, private router: Router) {
  }

  getQuestions(): Observable<Questions[]> {
    return this.http.get<Questions[]>(this.base_url);
  }

  getQuestion(id: number): Observable<Questions> {
    return this.http.get<Questions>(`${this.base_url}/${id}/`);
  }

  deleteQuestion(id:number): Observable<any> {
    return this.http.delete(`${this.base_url}/${id}/`);
  }

  updateQuestion(question: Questions): Observable<Questions> {
    return this.http.put<Questions>(`${this.base_url}/${question.id}/`, question);
  }

  addQuestion(question: Questions): Observable<Questions> {
    return this.http.post<Questions>(`${this.base_url}/`, question);
  }
}
