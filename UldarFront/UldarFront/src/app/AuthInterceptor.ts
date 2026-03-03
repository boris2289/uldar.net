import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";

@Injectable()
export class AuthInterceptor implements HttpInterceptor{
    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const access=localStorage.getItem('access')
        if (access){
            const newReq=req.clone({
                headers:req.headers.append('Authorization',`Bearer ${access}`)
            })
            return next.handle(newReq);
        }
        return next.handle(req);
    }
}