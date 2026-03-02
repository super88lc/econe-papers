'use client';

import { useState } from 'react';
import { DayPapers, Paper } from '@/types';
import PaperCard from './PaperCard';

interface DaySectionProps {
  dayPapers: DayPapers;
  selectedCategory: string;
}

export default function DaySection({ dayPapers, selectedCategory }: DaySectionProps) {
  const [showAll, setShowAll] = useState(false);
  
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
  
  // 显示逻辑：默认显示前5篇，点击"更多"展开全部
  const displayPapers = showAll ? filteredPapers : filteredPapers.slice(0, 5);
  const hasMore = filteredPapers.length > 5;
  
  return (
    <section className="mb-6">
      <div className="flex items-center gap-3 mb-3">
        <div className="h-px flex-1 bg-gray-200"></div>
        <h2 className="text-sm font-medium text-gray-500">
          📅 {dateStr} 精选 {filteredPapers.length} 篇
          {dayPapers.total > filteredPapers.length && (
            <span className="text-gray-400"> (共{dayPapers.total}篇)</span>
          )}
        </h2>
        <div className="h-px flex-1 bg-gray-200"></div>
      </div>
      
      {displayPapers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} />
      ))}
      
      {hasMore && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full py-3 mt-2 text-center text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
        >
          {showAll ? '▲ 收起' : `▼ 显示更多 ${filteredPapers.length - 10} 篇`}
        </button>
      )}
    </section>
  );
}
