import { Component, OnInit } from '@angular/core';
import { Users, users_list } from '../../../test_backend/users';
import { ActivatedRoute, Router } from '@angular/router';
import { JwtHelperService } from "@auth0/angular-jwt";
import { ServiceService } from 'src/app/services/service.service';

@Component({
  selector: 'app-user-page',
  templateUrl: './user-page.component.html',
  styleUrls: ['./user-page.component.css'],
})
export class UserPageComponent implements OnInit {
  user: Users | undefined;
  tokenPayload: any;
  usernameFromToken: string | undefined

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private service: ServiceService,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {
    const routeParams = this.route.snapshot.paramMap;
    const usernameFromRoute = String(routeParams.get('username'));
    this.service.getUser(usernameFromRoute).subscribe(
      (user) => {
        this.user = user;
      },
      (error) => {
        this.router.navigateByUrl(`nouserfound`);
      }
    );
    let token = localStorage.getItem('access');
    this.getTokenDecoded(token!);
    this.usernameFromToken = JSON.parse(this.tokenPayload).user;
  }

  getTokenDecoded(token: string) {
    this.tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
  }
}
