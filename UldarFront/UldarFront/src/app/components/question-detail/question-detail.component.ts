import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Questions, Tags, Users, Comments, QuestionDetailResponse } from 'src/app/models';
import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';
import { JwtHelperService } from "@auth0/angular-jwt";


@Component({
  selector: 'app-question-detail',
  templateUrl: './question-detail.component.html',
  styleUrls: ['./question-detail.component.css']
})

export class QuestionDetailComponent implements OnInit {

  question?: Questions;
  comments: Comments[] = [];
  tags: Tags[] = [];
  tagsForQuestion: Tags[] = [];
  user?: Users;

  commentText: string = "";
  isAuthenticated: boolean = false;

  
  tokenPayload: any;
  usernameFromToken?: number;

  constructor(
    private route: ActivatedRoute,
    private questionService: QuestionsService,
    private tagService: ServiceService,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {
    this.getUsernameFromTokenDecoded();

    console.log(this.usernameFromToken)

    const token = localStorage.getItem("access");

    if (token) {
      const helper = new JwtHelperService();
      this.isAuthenticated = !helper.isTokenExpired(token);
    }

    const slug = this.route.snapshot.paramMap.get('slug');
    if (!slug) return;

    this.questionService.getQuestion(slug).subscribe((response: QuestionDetailResponse) => {

      const q = response.question;

      this.question = q;
      this.comments = response.comments;
      this.tags = response.tags;

      this.tagsForQuestion = this.tags.filter(tag =>
        q.tag.includes(tag.id)
      );

      this.tagService.getUser(q.author).subscribe(user => {
        this.user = user;
        console.log(user)
      });

    });
  }

  

  postComment() {
    if (!this.commentText.trim()) return;

    const slug = this.route.snapshot.paramMap.get('slug');

    const data = {
      text: this.commentText,
      author: Number(this.usernameFromToken),
      question: this.question?.id
    };

    this.tagService.addComment(slug!, data).subscribe(res => {
      this.comments.push(res);
      this.commentText = "";
    });
  }

  getUsernameFromTokenDecoded() {

    const token = localStorage.getItem('access');

    if (!token) return;

    const decoded = this.jwtHelper.decodeToken(token);

    console.log("Token payload:", decoded);

    this.usernameFromToken = decoded.user_id;

    console.log(this.usernameFromToken)

  }
}