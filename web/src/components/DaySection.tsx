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
  
  // 获取当天全部论文并按评分排序（从高到低）
  const allPapers = [...dayPapers.papers].sort(
    (a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0)
  );
  
  // 分类筛选（支持多字段匹配，如"金融/计量"匹配"金融"）
  const filteredPapers = selectedCategory === '全部' 
    ? allPapers 
    : allPapers.filter(p => p.researchField.includes(selectedCategory));
  
  if (filteredPapers.length === 0) return null;
  
  const date = new Date(dayPapers.date);
  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  // 统计信息
  const totalPapers = allPapers.length;
  const highRatedCount = allPapers.filter(p => (p.scores?.overall || 0) >= 8).length;
  const mediumRatedCount = allPapers.filter(p => {
    const s = p.scores?.overall || 0;
    return s >= 6 && s < 8;
  }).length;
  
  // 按分类统计
  const categoryCount: Record<string, number> = {};
  allPapers.forEach(p => {
    const field = p.researchField.split('/')[0]; // 取第一个分类
    categoryCount[field] = (categoryCount[field] || 0) + 1;
  });
  const topCategories = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
  
  // 显示逻辑：默认显示前5篇，点击"更多"展开全部（按评分排序）
  const displayPapers = showAll ? filteredPapers : filteredPapers.slice(0, 5);
  const hasMore = filteredPapers.length > 5;
  
  return (
    <section className="mb-8">
      {/* 每日总结 */}
      <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a4a73] rounded-lg p-4 mb-4 text-white">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold">📅 {dateStr}</h2>
          <span className="text-2xl font-bold">{totalPapers}篇</span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="bg-white/10 rounded-lg p-2">
            <div className="text-yellow-400 font-bold text-lg">{highRatedCount}</div>
            <div className="text-white/70">高分推荐</div>
          </div>
          <div className="bg-white/10 rounded-lg p-2">
            <div className="text-green-400 font-bold text-lg">{mediumRatedCount}</div>
            <div className="text-white/70">中等评分</div>
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
      
      {/* 论文列表 */}
      {displayPapers.map((paper, idx) => (
        <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
      ))}
      
      {hasMore && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full py-3 mt-2 text-center text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
        >
          {showAll ? '▲ 收起' : `▼ 显示更多 ${filteredPapers.length - 5} 篇`}
        </button>
      )}
    </section>
  );
}
