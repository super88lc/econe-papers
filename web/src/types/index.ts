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
  | '全部'
  | '金融'
  | '计量'
  | '理论'
  | '宏观'
  | '微观'
  | '行为'
  | '产业'
  | '环境'
  | '劳动'
  | '其他';

export const CATEGORIES: Category[] = [
  '全部', '金融', '计量', '理论', '宏观', '微观', '行为', '产业', '环境', '劳动', '其他'
];
