import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';
import { Users, Questions, Tags } from 'src/app/models';
import { JwtHelperService } from "@auth0/angular-jwt";

@Component({
  selector: 'app-edit-question',
  templateUrl: './edit-question.component.html',
  styleUrls: ['./edit-question.component.css']
})
export class EditQuestionComponent implements OnInit {

  question?: Questions;

  tags: Tags[] = [];

  id = 0;
  title = '';
  description = '';

  tag: number[] = [];
  selectedTagId = 0;

  tagName = '';
  codefield = '';

  author!: number;

  title_empty = false;
  description_empty = false;
  tag_empty = false;

  isCompleted = false;

  usernameFromToken?: string;

  constructor(
    private route: ActivatedRoute,
    private service: QuestionsService,
    private tagService: ServiceService,
    private router: Router,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {

    const slug = this.route.snapshot.paramMap.get('slug');

    if (!slug) {
      this.router.navigateByUrl('/questions');
      return;
    }

    this.getTokenDecoded();


    this.service.getQuestion(slug).subscribe((response) => {

    const question = response.question;

    this.question = question;

    this.id = question.id;
    this.title = question.title;
    this.description = question.description;
    this.tag = question.tag;

    this.selectedTagId = question.tag[0];


      this.tagService.getTags().subscribe((tags) => {

        this.tags = tags;

        const tag = tags.find(t => t.id === this.selectedTagId);

        if (tag) {
          this.tagName = tag.name;
        }

      });

    });

  }

  check() {
    this.title_empty = this.title === '';
    this.description_empty = this.description === '';
    this.tag_empty = this.selectedTagId === 0;

    this.isCompleted =
      !this.title_empty &&
      !this.description_empty &&
      !this.tag_empty;
  }

  recheck() {
    this.isCompleted = false;
  }

  editquestion() {

    const updatedQuestion: Questions = {

      id: this.id,
      title: this.title,
      description: this.description,
      slug: this.title.toLowerCase().replace(/\s+/g, '-'),
      author: this.author,
      tag: [this.selectedTagId],
      created_at: new Date(),
      updated_at: new Date(),
      is_active: true,

    };

    this.service.updateQuestion(updatedQuestion).subscribe(() => {

      this.router.navigateByUrl(`/questions/${updatedQuestion.slug}`);

    });

  }

  getTokenDecoded() {

    const token = localStorage.getItem('access');

    if (token) {
      const payload = this.jwtHelper.decodeToken(token);
      this.usernameFromToken = payload.user;
    }

  }

}