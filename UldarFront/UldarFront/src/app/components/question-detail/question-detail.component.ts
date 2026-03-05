import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Questions, Messages, Tags, Users } from 'src/app/models';
import { JwtHelperService } from "@auth0/angular-jwt";

import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';

@Component({
  selector: 'app-question-detail',
  templateUrl: './question-detail.component.html',
  styleUrls: ['./question-detail.component.css'],
})
export class QuestionDetailComponent implements OnInit {
  slug: string | null = null;
  question: Questions | undefined;
  messages: Messages[] = [];
  tags: Tags[] | undefined;
  users: Users[] | undefined;

  user: Users = {
    id: 0,
    first_name: "Someone",
    second_name: "Someone",
    email: "Something",
  };

  tag: Tags = {
    id: 0,
    name: "None",
    description: "Something"
  };

  logged = false;
  usernameFromToken: string | undefined;

  body: string = '';
  code: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private questionsService: QuestionsService,
    private messageService: ServiceService,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {
    const access = localStorage.getItem('access');
    if (access) this.logged = true;

    this.getTokenDecoded();

    const slug = this.route.snapshot.paramMap.get('slug');

    if (!slug) {
      this.router.navigateByUrl('/no-question-found');
      return;
    }

    this.slug = slug;

    // Получаем вопрос по slug
    this.questionsService.getQuestion(this.slug).subscribe(
      (question) => {
        this.question = question;

        // Получаем сообщения для вопроса
        // this.messageService.getMessages(this.slug!).subscribe((messages) => {
        //   this.messages = messages.sort(
        //     (m1, m2) => new Date(m2.updated).getTime() - new Date(m1.updated).getTime()
        //   );
        // });

        // Получаем теги
        // this.messageService.getTags().subscribe((tags) => {
        //   this.tags = tags;
        //   const tag = tags.find(t => t.id === this.question?.tag);
        //   if (tag) this.tag = tag;
        // });

        // Получаем пользователей
        // this.messageService.getUsers().subscribe((users) => {
        //   this.users = users;
        //   const user = users.find(u => u.id === this.question?.user);
        //   if (user) this.user = user;
        // });
      },
      (error) => {
        this.router.navigateByUrl('/no-question-found').then();
      }
    );
  }

  edit() {
    this.router.navigateByUrl(`/questions/${this.slug}/update`).then();
  }

  delete() {
    if (!this.slug) return;
    this.questionsService.deleteQuestion(this.slug).subscribe(() => {
      console.log("deleted");
      this.router.navigateByUrl('/questions').then();
    });
  }

  getTokenDecoded() {
    const token = localStorage.getItem('access');
    if (token) {
      const payload: any = this.jwtHelper.decodeToken(token);
      this.usernameFromToken = payload.user;
    }
  }

  addMessage() {
    if (!this.slug) return;
    if (this.body.trim().length === 0) {
      alert('You must enter at least the body of the message!');
      return;
    }

    this.messageService.getUser(this.usernameFromToken!).subscribe(user => {
      const newMessage = {
        body: this.body,
        code_field: this.code,
        question_slug: this.slug,
        user_id: user.id
      };

      // this.messageService.addMessage(this.slug!, newMessage).subscribe(() => {
      //   location.reload();
      // });
    });
  }
}