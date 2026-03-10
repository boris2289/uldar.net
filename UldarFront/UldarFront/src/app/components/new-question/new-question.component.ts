import { Component, OnInit } from '@angular/core';
import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';
import { Router } from "@angular/router";
import { Tags, Questions } from 'src/app/models';
import { JwtHelperService } from "@auth0/angular-jwt";

@Component({
  selector: 'app-new-question',
  templateUrl: './new-question.component.html',
  styleUrls: ['./new-question.component.css'],
})
export class NewQuestionComponent implements OnInit {

  tagInputs: string[] = [''];
  tagIds: number[] = [];

  question?: Questions;

  tags: Tags[] = [];

  title = '';
  description = '';
  slug = '';

  tag!: number;
  newTagName = '';

  author!: number;

  title_empty = false;
  description_empty = false;
  tag_empty = false;

  isCompleted = false;

  tokenPayload: any;
  usernameFromToken?: number;

  constructor(
    private service: QuestionsService,
    private tagService: ServiceService,
    private router: Router,
    private jwtHelper: JwtHelperService
  ) {}

  ngOnInit(): void {

    this.getUsernameFromTokenDecoded();

    this.loadTags();

    if (this.usernameFromToken == undefined) {
      this.router.navigateByUrl('questions');
    }

  }

  loadTags(){
    this.tagService.getTags().subscribe((tags)=>{
      this.tags = tags;
    });
  }

  check() {

    this.title_empty = this.title === '';
    this.description_empty = this.description === '';

    this.tag_empty = this.tagInputs.length === 0;

    if (!this.title_empty && !this.description_empty && !this.tag_empty) {
      this.isCompleted = true;
    }

  }

  recheck() {
    this.isCompleted = false;
  }

  newquestion() {

  this.tagIds = [];

  let requests: any[] = [];

  this.tagInputs.forEach(tagName => {

    const clean = tagName.replace('#', '').trim();

    if (!clean) return;

    const existing = this.tags.find(t => t.name.toLowerCase() === clean.toLowerCase());

    if (existing) {
      this.tagIds.push(existing.id);
    } else {

      const req = this.tagService.createTag(clean);

      requests.push(req);

    }

  });

  if (requests.length > 0) {

    requests.forEach(r => {
      r.subscribe((tag: Tags) => {

        this.tagIds.push(tag.id);

      });
    });

  }

  setTimeout(() => {

    this.question = {
      id: 0,
      title: this.title,
      description: this.description,
      slug: this.title,
      author: Number(this.usernameFromToken),
      tag: this.tagIds,
      created_at: new Date(),
      updated_at: new Date(),
      is_active: true
    };

    console.log(this.question);

    this.service.addQuestion(this.question!).subscribe();

    this.router.navigateByUrl('questions');

  }, 500);

}

  addTag() {
  this.tagInputs.push('');
  }

  createTag() {

    if (!this.newTagName) return;

    this.tagService.createTag(this.newTagName).subscribe(tag => {

      console.log("Tag created:", tag);

      this.tags.push(tag);

      this.tag = tag.id;

      this.newTagName = '';

    });

  }

  trackByIndex(index: number): number {
  return index;
}

  getUsernameFromTokenDecoded() {

    const token = localStorage.getItem('access');

    if (!token) return;

    const decoded = this.jwtHelper.decodeToken(token);

    console.log("Token payload:", decoded);

    this.usernameFromToken = decoded.user_id;

  }

}