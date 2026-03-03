import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Tags, tags_list } from 'src/test_backend/tags';
import { Questions, question_list } from 'src/test_backend/questions';
import { ServiceService } from 'src/app/services/service.service';
import { QuestionsService } from 'src/app/services/questions.service';

@Component({
  selector: 'app-tag-detail',
  templateUrl: './tag-detail.component.html',
  styleUrls: ['./tag-detail.component.css'],
})
export class TagDetailComponent implements OnInit {
  tag: Tags | undefined;
  questions: Questions[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private service: ServiceService,
    private questionService: QuestionsService
  ) {}

  ngOnInit(): void {
    const routeParams = this.route.snapshot.paramMap;
    const tagIDFromRoute = Number(routeParams.get('tagID'));
    const tagNameFromRoute = String(routeParams.get('tagName'));
    this.service.getTag(tagNameFromRoute).subscribe(
      (tag) => {
        this.tag = tag;
        this.questionService.getQuestions().subscribe(
          (questions) =>
            (this.questions = questions.filter((question) => {
              return question.tag === this.tag?.id;
            }))
        );
      },
      (error) => {
        this.router.navigateByUrl(`notagfound`);
      }
    );
  }
}
