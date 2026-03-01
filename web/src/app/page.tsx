'use client';

import { useState, useEffect, useCallback } from 'react';
import Header from '@/components/Header';
import DaySection from '@/components/DaySection';
import Footer from '@/components/Footer';
import { DayPapers, Category } from '@/types';

export default function Home() {
  const [category, setCategory] = useState<Category>('全部');
  const [days, setDays] = useState<DayPapers[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
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
  
  // Infinite scroll
  useEffect(() => {
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
  }, [loadMore]);
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header 
        selectedCategory={category} 
        onCategoryChange={setCategory} 
      />
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
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
      </main>
      
      <Footer />
    </div>
  );
}
