import { Component, OnInit } from '@angular/core';
import { Questions, Tags } from 'src/app/models';
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
  activeTab: 'active' | 'archive' = 'active';
  filteredQuestions: Questions[] = [];
  questions: Questions[] = [];
  tags: Tags[] = [];

  constructor(private service: QuestionsService,
    private tagService: ServiceService
  ) {}

  ngOnInit(): void {

    this.tagService.getTags().subscribe(tags => {
    this.tags = tags;
  });

    const access=localStorage.getItem('access');
    if (access) this.logged=true;

    this.service.getQuestions().subscribe((questions) => {
      this.questions = questions
        .sort((q1, q2) => {
          return (
            new Date(q2.created_at).getTime() -
            new Date(q1.created_at).getTime()
          );
        });
      this.applyFilter();
    });
  }
  alert(){
    this.alertF=true;
  }



  setTab(tab: 'active' | 'archive') {
  this.activeTab = tab;
  this.applyFilter();
  }

  applyFilter() {
    this.filteredQuestions = this.activeTab === 'active'
      ? this.questions.filter(q => q.is_active)
      : this.questions.filter(q => !q.is_active);
  }

getTagName(tagId: number): string {
  return this.tags.find(t => t.id === tagId)?.name ?? '';
}
}

