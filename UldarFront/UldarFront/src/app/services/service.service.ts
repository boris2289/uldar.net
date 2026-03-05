import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { JwtHelperService } from "@auth0/angular-jwt";
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthToken } from '../models';
import { Router } from "@angular/router";
import { Tags, TagDetailResponse,Comments, Users, } from '../models';

const helper = new JwtHelperService();

@Injectable({
  providedIn: 'root',
})

export class ServiceService {
  //private apiURL = 'http://localhost:5000';
  private base_url='http://127.0.0.1:8000/api/';

  constructor(private http: HttpClient, private router: Router) {
  }

  getTags(): Observable<Tags[]> {
    return this.http.get<Tags[]>(`${this.base_url}tags/list`);
  }

  // getTag(id: number): Observable<Tags> {
  //   return this.http.get<Tags>(`${this.base_url}/tags/${id}/`);
  // }

  getTag(name: string): Observable<TagDetailResponse> {
    return this.http.get<TagDetailResponse>(`${this.base_url}tags/${name}/retrieve`);
  }

  createTag(name: string): Observable<Tags> {
    return this.http.post<Tags>(`${this.base_url}tags/create`, {
      name: name
    });
  }
  

  addComment(slug : string, data: any): Observable<Comments> {
    return this.http.post<Comments>(`${this.base_url}questions/${slug}/create_comment`, data)
  }

  getUsers(): Observable<Users[]> {
    return this.http.get<Users[]>(`${this.base_url}/users`);
  }

  getUser(id : number): Observable<Users> {
    return this.http.get<Users>(`${this.base_url}users/${id}/`);
  }

  login(email: string, password: string) {
    return this.http.post<any>(`${this.base_url}login/`, {
      email: email,
      password: password
    });
  }

  register(data: any): Observable<Users> {
    return this.http.post<Users>(`${this.base_url}register/`, data)
  }

  changePassword(username: string, data: any):Observable<null>{
    return this.http.put<any>(`${this.base_url}/users/${username}/change_password/`,data);
  }

  isExpiredToken(token: string | null): boolean {
    if (!token) {
      token = localStorage.getItem('access');
    }
    if (!token) {
      return true;
    }

    const date = helper.getTokenExpirationDate(token);

    if (date === undefined) return false;
    if (date) {
      return !(date.valueOf() > new Date().valueOf());
    }
    return true;
  }
}
