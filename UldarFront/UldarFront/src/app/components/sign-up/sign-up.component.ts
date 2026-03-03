
import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Users } from '../../../test_backend/users';
import { ServiceService } from "../../services/service.service";
import Validation from '../../utils/validation'
import { Router } from '@angular/router';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.css']
})
export class SignUpComponent implements OnInit {

  form: FormGroup = new FormGroup({
    firstname: new FormControl(''),
    lastname: new FormControl(''),
    age: new FormControl(''),
    username: new FormControl(''),
    email: new FormControl(''),
    password: new FormControl(''),
    confirmPassword: new FormControl(''),
  });
  submitted = false;

  data: {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
    password2: string;
    age: string;
  } | undefined

  constructor(private formBuilder: FormBuilder, private service: ServiceService, private route : Router) { }

  ngOnInit(): void {
    this.form = this.formBuilder.group(
      {
        firstname: ['', Validators.required],
        lastname: ['', Validators.required],
        age: ['', Validators.required],
        username: [
          '',
          [
            Validators.required,
            Validators.minLength(6),
            Validators.maxLength(20)
          ]
        ],
        email: ['', [Validators.required, Validators.email]],
        password: [
          '',
          [
            Validators.required,
            Validators.minLength(6),
            Validators.maxLength(40)
          ]
        ],
        confirmPassword: ['', Validators.required],
      },
      {
        validators: [Validation.match('password', 'confirmPassword')]
      }
    );
  }

  get f(): { [key: string]: AbstractControl } {
    return this.form.controls;
  }

  onSubmit(): void {
    this.submitted = true;
    if (this.form.invalid) {
      return;
    }
    this.data = {
      email: this.form.get('email')?.value,
      username: this.form.get('username')?.value,
      first_name: this.form.get('firstname')?.value,
      last_name: this.form.get('lastname')?.value,
      password: this.form.get('password')?.value,
      password2: this.form.get('password')?.value,
      age: this.form.get('age')?.value,
    }
    this.service.register(this.data).subscribe(user => {
      console.log(user)})
    console.log(this.data);
  }
  onReset(): void {
    this.submitted = false;
    this.form.reset();
  }
  
  goToLogin() {
    this.route.navigateByUrl('login');
  }
}
