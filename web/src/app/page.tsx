'use client';

import { useState, useEffect, useCallback } from 'react';
import Header from '@/components/Header';
import DaySection from '@/components/DaySection';
import Footer from '@/components/Footer';
import PaperCard from '@/components/PaperCard';
import { DayPapers, Paper, Category } from '@/types';

export default function Home() {
  const [category, setCategory] = useState<Category>('全部');
  const [days, setDays] = useState<DayPapers[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  // 收集所有分类论文（用于分类视图）
  const [categoryPapers, setCategoryPapers] = useState<Paper[]>([]);
  const [showCategoryView, setShowCategoryView] = useState(false);
  
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    const lastDate = days.length > 0 
      ? days[days.length - 1].date 
      : undefined;
    
    try {
      const params = new URLSearchParams();
      if (lastDate) {
        params.set('before', lastDate);
        params.set('limit', '30');
      }
      
      const res = await fetch(`/api/papers?${params}`);
      const data = await res.json();
      
      if (data.days && data.days.length > 0) {
        setDays(prev => [...prev, ...data.days]);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Failed to load papers:', error);
    } finally {
      setLoading(false);
    }
  }, [days, loading, hasMore]);
  
  // 当分类变化时，收集该分类的所有论文
  useEffect(() => {
    if (category === '全部') {
      setShowCategoryView(false);
      setCategoryPapers([]);
    } else {
      // 收集所有天数中该分类的论文
      const papers: Paper[] = [];
      days.forEach(day => {
        day.papers.forEach(paper => {
          if (paper.researchField.includes(category)) {
            papers.push(paper);
          }
        });
      });
      // 按评分排序
      papers.sort((a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0));
      setCategoryPapers(papers);
      setShowCategoryView(true);
    }
  }, [category, days]);
  
  // Initial load
  useEffect(() => {
    const init = async () => {
      const res = await fetch('/api/papers');
      const data = await res.json();
      if (data.days) {
        setDays(data.days);
      }
    };
    init();
  }, []);
  
  // Infinite scroll (仅用于日期视图)
  useEffect(() => {
    if (showCategoryView) return; // 分类视图不需要无限滚动
    
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY 
        >= document.body.offsetHeight - 500
      ) {
        loadMore();
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadMore, showCategoryView]);
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header 
        selectedCategory={category} 
        onCategoryChange={setCategory} 
      />
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
        {showCategoryView ? (
          // 分类视图：显示该分类的所有论文
          <section>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200"></div>
              <h2 className="text-sm font-medium text-gray-500">
                📂 {category}精选 {categoryPapers.length} 篇
              </h2>
              <div className="h-px flex-1 bg-gray-200"></div>
            </div>
            
            {categoryPapers.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                暂无{category}分类的论文
              </div>
            ) : (
              categoryPapers.map((paper, idx) => (
                <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
              ))
            )}
          </section>
        ) : (
          // 日期视图：按日期分组显示
          <>
            {days.map((dayPapers) => (
              <DaySection 
                key={dayPapers.date} 
                dayPapers={dayPapers} 
                selectedCategory={category}
              />
            ))}
            
            {loading && (
              <div className="text-center py-8 text-gray-500">
                加载中...
              </div>
            )}
            
            {!hasMore && days.length > 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">
                已加载全部历史
              </div>
            )}
          </>
        )}
      </main>
      
      <Footer />
    </div>
  );
}
