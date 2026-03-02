export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  categories: string[];
  published: string;
  updated: string;
  pdfUrl: string;
  
  // AI 处理后
  chineseTitle: string;
  chineseAbstract: string;
  researchField: string;
  keywords: string[];
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
  | '宏观'
  | '微观'
  | '计量'
  | '金融'
  | '行为'
  | '产业'
  | '环境'
  | '劳动'
  | '其他';

export const CATEGORIES: Category[] = [
  '全部', '宏观', '微观', '计量', '金融', '行为', '产业', '环境', '劳动', '其他'
];
