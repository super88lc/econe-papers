'use client';

import { useState, useEffect } from 'react';
import { DayPapers, Paper } from '@/types';
import PaperCard from './PaperCard';

interface DaySectionProps {
  dayPapers: DayPapers;
  selectedCategory: string;
}

export default function DaySection({ dayPapers, selectedCategory }: DaySectionProps) {
  const [showAll, setShowAll] = useState(false);
  
  const allPapers = [...dayPapers.papers].sort(
    (a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0)
  );
  
  const filteredPapers = selectedCategory === 'All' 
    ? allPapers 
    : allPapers.filter(p => p.researchField.includes(selectedCategory));
  
  if (filteredPapers.length === 0) return null;
  
  const date = new Date(dayPapers.date);
  const dateStr = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  const totalPapers = allPapers.length;
  const highRatedCount = allPapers.filter(p => (p.scores?.overall || 0) >= 6.5).length;
  
  const categoryCount: Record<string, number> = {};
  allPapers.forEach(p => {
    const field = p.researchField.split('/')[0];
    categoryCount[field] = (categoryCount[field] || 0) + 1;
  });
  const topCategories = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
  
  const displayPapers = showAll ? filteredPapers : filteredPapers.slice(0, 5);
  const hasMore = filteredPapers.length > 5;
  
  return (
    <section className="mb-8">
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a4a73] rounded-lg p-4 mb-4 text-white">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold">📅 {dateStr}</h2>
          <span className="text-2xl font-bold">{totalPapers}</span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="bg-white/10 rounded-lg p-2">
            <div className="text-yellow-400 font-bold text-lg">{highRatedCount}</div>
            <div className="text-white/70">Recommended</div>
          </div>
          <div className="bg-white/10 rounded-lg p-2 col-span-2">
            <div className="flex flex-wrap gap-1">
              {topCategories.map(([cat, count]) => (
                <span key={cat} className="bg-white/20 px-2 py-0.5 rounded text-xs">
                  {cat}: {count}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {displayPapers.map((paper, idx) => (
        <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
      ))}
      
      {hasMore && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full py-3 mt-2 text-center text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
        >
          {showAll ? '▲ Show Less' : `▼ Show More ${filteredPapers.length - 5} Papers`}
        </button>
      )}
    </section>
  );
}
