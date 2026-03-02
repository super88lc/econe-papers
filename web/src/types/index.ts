export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  categories: string[];
  published: string;
  updated: string;
  pdfUrl: string;
  
  chineseTitle: string;
  chineseAbstract: string;
  researchField: string;
  keywords: string[];
  tags?: string[];
  scores: {
    overall: number;
    novelty: number;
    quality: number;
    readability: number;
  };
  summary: string;
}

export interface DayPapers {
  date: string;
  papers: Paper[];
  total: number;
}

export type Category = 
  | 'All'
  | 'Finance'
  | 'Econometrics'
  | 'Theory'
  | 'Macro'
  | 'Micro'
  | 'Behavioral'
  | 'Industrial'
  | 'Environmental'
  | 'Labor'
  | 'Other';

export const CATEGORIES: Category[] = [
  'All', 'Finance', 'Econometrics', 'Theory', 'Macro', 'Micro', 'Behavioral', 'Industrial', 'Environmental', 'Labor', 'Other'
];
