import { Messages } from './messages';

export interface Questions {
  id: number;
  title: string;
  body: string;
  user: number;
  tag: number;
  created: Date;
  updated: Date;
  is_active: boolean;
  code_field: string;
}

export let question_list = [
  {
    id: 1,
    title: 'How to play football?',
    body: 'Hello! I am new to football and do not know how to play it. Can anybody help me?',
    user: 1,
    tag: 1,
    created_date: new Date('2025-01-17T15:24:00'),
    updated_date: new Date('2025-01-17T15:34:10'),
    is_active: true,
    code_field: '',
  },
  {
    id: 2,
    title: 'How to play basketball?',
    body: 'Hello! I am new to basketball and do not know how to play it. Can anybody help me?',
    user: 2,
    tag: 3,
    created_date: new Date('2025-01-21T12:21:00'),
    updated_date: new Date('2025-01-21T12:23:45'),
    is_active: false,
    code_field: '',
  },
];
