import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Route, Router } from '@angular/router';
import { Questions,Messages,Tags,Users } from 'src/app/models';
import { JwtHelperService } from "@auth0/angular-jwt";

import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';

@Component({
  selector: 'app-question-detail',
  templateUrl: './question-detail.component.html',
  styleUrls: ['./question-detail.component.css'],
})
export class QuestionDetailComponent implements OnInit {
  id=0;
  messages: Messages[] = [];
  tags: Tags[] | undefined;
  users: Users[] | undefined;
  user: Users = {
    id:0,
    first_name:"Someone",
    second_name:"Someone",
    username:"Someone",
    email:"Something",
    bio:"Something",
    avatar:"Something"
  }
  question: Questions | undefined;
  tag: Tags ={
    id:0,
    name:"None",
    description:"Something"
  }
  logged=false;

  usernameFromToken: string | undefined;


  body: string = ''
  code: string = ''


  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private service: QuestionsService,
    private messageService: ServiceService,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {

    const access=localStorage.getItem('access');
    if (access) this.logged=true;

    this.getTokenDecoded();

    const routeParams = this.route.snapshot.paramMap;
    const questionIdFromRoute = Number(routeParams.get('questionID'));

    this.service.getQuestion(questionIdFromRoute).subscribe(
      (question) => {
        this.question = question;
        this.id=question.id;

        this.messageService.getMessages(questionIdFromRoute).subscribe((messages) => {
          this.messages = messages;
          this.messages.sort((m1, m2) => {
            return (
              new Date(m2.updated).getTime() -
              new Date(m1.updated).getTime()
            );
          });
        });
      },
      (error) => {
        this.router.navigateByUrl(`no-question-found`).then();
      }
    );
    this.messageService.getTags().subscribe((tags) => {
      this.tags = tags;
      for (let i=0;i<tags.length;i++){
        if (tags[i].id==this.question?.tag) this.tag=tags[i];
      }
    });
    this.messageService.getUsers().subscribe((users) => {
      this.users = users;
      for (let i=0;i<users.length;i++){
        if (users[i].id==this.question?.user) this.user=users[i];
      }
    });
  }

  edit() {
    this.router.navigateByUrl(`/questions/${this.question?.id}/edit`).then();
  }
  delete(){
    this.service.deleteQuestion(this.id).subscribe((data)=>{console.log("deleted")});
    this.router.navigateByUrl(`/questions`).then();
  }

  getTokenDecoded() {
    let token = localStorage.getItem('access');
    if (token) {
      let tokenPayload = JSON.stringify(this.jwtHelper.decodeToken(token));
      this.usernameFromToken = JSON.parse(tokenPayload).user;
    }
  }

  addMessage() {
    if (this.body.length <= 0) {
      alert('You must enter at least body of message!')
      return;
    }
    let id: number = 0;
    let newMessage = {}
    this.messageService.getUser(this.usernameFromToken!).subscribe(user => {
      if (user.username == this.usernameFromToken) {
        id = user.id;
      }
      newMessage = {
        body: this.body,
        code_field: this.code,
        question: this.question?.id!,
        user_id: id
      }
      console.log(newMessage)
      this.messageService.addMessage(this.question?.id!, newMessage).subscribe(message => {
        console.log(message)
      })
      location.reload()
    })


  }
}
