import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ServiceService} from 'src/app/services/service.service';
import {Location} from "@angular/common";
import { JwtHelperService } from "@auth0/angular-jwt";

@Component({
  selector: 'app-password-change',
  templateUrl: './password-change.component.html',
  styleUrls: ['./password-change.component.css']
})
export class PasswordChangeComponent implements OnInit {

  old_password='';
  password='';
  password2='';
  username = '';

  isCompleted=false;
  oldEmpty=false;
  new1Empty=false;
  new2Empty=false;
  same=true;

  usernameFromToken: string | undefined

  constructor(private _service:ServiceService,
              private route: ActivatedRoute,
              private _location: Location,
              private jwtHelper: JwtHelperService) { }

  ngOnInit(): void {

    const routeParams = this.route.snapshot.paramMap;
    this.username = String(routeParams.get('username'));
    this.getUsernameFromTokenDecoded();
    if (this.username != this.usernameFromToken) {
      alert('You do not have permissions for this user!!!')
      this._location.back()
    }

  }

  check() {
    if (this.old_password!='' && this.password!='' && (this.password==this.password2)) this.isCompleted = true;
    else{
      if (this.old_password=='') this.oldEmpty=true;
      if (this.password=='') this.new1Empty=true;
      if (this.password2=='') this.new2Empty=true;
      if (this.password!=this.password2) this.same=false;
    }

  }
  recheck() {
    this.isCompleted=false;
  }
  changePassword(){
    let data =  {
      old_password: this.old_password,
      password: this.password,
      password2: this.password2
    }
    console.log(data)
    this._service.changePassword(this.username,data).subscribe()
    this._location.back()
  }

  getUsernameFromTokenDecoded() {
    let token = localStorage.getItem('access');
    if (token) {
      let tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
      this.usernameFromToken = JSON.parse(tokenPayload).user;
    }
  }

}
