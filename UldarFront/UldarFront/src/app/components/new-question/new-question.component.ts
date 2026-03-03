import { Component, OnInit } from '@angular/core';
import { Tags, tags_list } from '../../../test_backend/tags';
import { Questions } from 'src/test_backend/questions';
import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';
import { Users } from 'src/test_backend/users';
import { Router } from "@angular/router";

import { JwtHelperService } from "@auth0/angular-jwt";

@Component({
  selector: 'app-new-question',
  templateUrl: './new-question.component.html',
  styleUrls: ['./new-question.component.css'],
})
export class NewQuestionComponent implements OnInit {
  question: Questions | undefined;
  tags: Tags[] = [];
  user: Users | undefined;
  title = '';
  body = '';
  tag: string = '';
  codefield = '';
  title_empty = false;
  body_empty = false;
  tag_empty = false;
  isCompleted = false;
  questionsNumber=0;

  tokenPayload: any;
  usernameFromToken: string | undefined;

  constructor(
    private service: QuestionsService,
    private tagService: ServiceService,
    private router: Router,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {
    this.getUsernameFromTokenDecoded();
    this.tagService.getTags().subscribe((tags) => (this.tags = tags));
    this.service.getQuestions().subscribe((questions) => {this.questionsNumber = questions.length});
    this.tagService.getUser(this.usernameFromToken!).subscribe(user => this.user = user)

    if (this.usernameFromToken == undefined) {
      this.router.navigateByUrl('questions').then()
    }
  }

  check() {
    this.title_empty = this.title == '';
    this.body_empty = this.body == '';
    this.tag_empty = this.tag == '';
    if (
      !this.title_empty &&
      !this.body_empty &&
      !this.tag_empty
    )
      this.isCompleted = true;
  }
  recheck() {
    this.isCompleted = false;
  }
  newquestion() {
    this.question = {
      id:this.questionsNumber+1,
      title: this.title,
      body: this.body,
      user: this.user?.id!,
      tag: +this.tag[0],
      created: new Date(),
      updated: new Date(),
      is_active: true,
      code_field: this.codefield
    };

    this.service.addQuestion(this.question!).subscribe((question) => {console.log(question)});
    this.router.navigateByUrl('questions').then();
  }
  back() {}

  getUsernameFromTokenDecoded() {
    let token = localStorage.getItem('access');
    if (token) {
      this.tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
      this.usernameFromToken = JSON.parse(this.tokenPayload).user;
    }
  }
}
