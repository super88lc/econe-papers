'use client';

import { DayPapers, Paper } from '@/types';
import PaperCard from './PaperCard';

interface DaySectionProps {
  dayPapers: DayPapers;
  selectedCategory: string;
}

export default function DaySection({ dayPapers, selectedCategory }: DaySectionProps) {
  const filteredPapers = selectedCategory === '全部' 
    ? dayPapers.papers 
    : dayPapers.papers.filter(p => p.researchField === selectedCategory);
  
  if (filteredPapers.length === 0) return null;
  
  const date = new Date(dayPapers.date);
  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  return (
    <section className="mb-6">
      <div className="flex items-center gap-3 mb-3">
        <div className="h-px flex-1 bg-gray-200"></div>
        <h2 className="text-sm font-medium text-gray-500">
          📅 {dateStr} 精选 {filteredPapers.length} 篇
        </h2>
        <div className="h-px flex-1 bg-gray-200"></div>
      </div>
      
      {filteredPapers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} />
      ))}
    </section>
  );
}
