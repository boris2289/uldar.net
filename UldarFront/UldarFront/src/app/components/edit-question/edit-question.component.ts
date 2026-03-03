import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { QuestionsService } from 'src/app/services/questions.service';
import { Questions } from 'src/test_backend/questions';
import { ServiceService } from 'src/app/services/service.service';
import { Tags } from 'src/test_backend/tags';
import { Users } from 'src/test_backend/users';
import { Router } from "@angular/router";

import { JwtHelperService } from "@auth0/angular-jwt";

@Component({
  selector: 'app-edit-question',
  templateUrl: './edit-question.component.html',
  styleUrls: ['./edit-question.component.css']
})
export class EditQuestionComponent implements OnInit {

  question: Questions | undefined;
  tags: Tags[] = [];
  id = 0;
  title = '';
  body = '';
  tag: number = -1;
  tagName: string = ''
  tagFromForm: string = ''
  codefield = '';
  user: Users | undefined;
  user_empty = false;
  title_empty = false;
  body_empty = false;
  tag_empty = false;
  isCompleted = false;

  usernameFromToken: string | undefined;

  constructor(private route: ActivatedRoute,private service: QuestionsService,private tagService: ServiceService,
              private router: Router, private jwtHelper: JwtHelperService) { }

  ngOnInit(): void {
    const routeParams = this.route.snapshot.paramMap;
    const questionId = Number(routeParams.get('questionID'));
    this.getTokenDecoded();
    this.tagService.getUser(this.usernameFromToken!).subscribe(user => this.user = user);
    this.service.getQuestion(questionId).subscribe((question) => {
        this.question = question;
        this.id=question.id
        this.title=question.title;
        this.body=question.body;
        this.tag=question.tag;
        this.codefield=question.code_field;
      })

    this.tagService.getTags().subscribe((tags) => {
      this.tags = tags;
      for (let i=0;i<this.tags.length;i++){
        if (this.tags[i].id==this.tag) {
          this.tagName = this.tags[i].name
          this.tags.splice(i, 1)
        }
      }
    });
  }

  check() {
    this.title_empty = this.title == '';
    this.body_empty = this.body == '';
    this.tag_empty = this.tag === -1;
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
  editquestion() {
    this.question = {
      id: this.id,
      title: this.title,
      body: this.body,
      user: this.user?.id!,
      tag: +this.tagFromForm[0],
      created: new Date(),
      updated: new Date(),
      is_active: true,
      code_field: this.codefield,
    };

    this.service.updateQuestion(this.question).subscribe((question) => {console.log(this.question);});
    this.router.navigateByUrl(`/questions/${this.question?.id}`)
  }

  getTokenDecoded() {
    let token = localStorage.getItem('access');
    if (token) {
      let tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
      this.usernameFromToken = JSON.parse(tokenPayload).user;
    }
  }

}
