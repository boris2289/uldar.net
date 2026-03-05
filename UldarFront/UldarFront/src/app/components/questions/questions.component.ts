import { Component, OnInit } from '@angular/core';
import { Questions } from 'src/app/models';
import { QuestionsService } from 'src/app/services/questions.service';
import { ServiceService } from 'src/app/services/service.service';

@Component({
  selector: 'app-questions',
  templateUrl: './questions.component.html',
  styleUrls: ['./questions.component.css'],
})
export class QuestionsComponent implements OnInit {
  logged=false;
  alertF=false;
  questions: Questions[] | undefined;

  constructor(private service: QuestionsService) {}

  ngOnInit(): void {

    const access=localStorage.getItem('access');
    if (access) this.logged=true;

    this.service.getQuestions().subscribe((questions) => {
      this.questions = questions;
      this.questions.sort((q1, q2) => {
        return (
          new Date(q2.created_at).getTime() -
          new Date(q1.created_at).getTime()
        );
      });
    });
  }
  alert(){
    this.alertF=true;
  }
}

