import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Users } from 'src/app/models';
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
    let token = localStorage.getItem('access');
    this.getTokenDecoded(token!);
    this.usernameFromToken = JSON.parse(this.tokenPayload).user;
  }

  getTokenDecoded(token: string) {
    this.tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
  }
}
