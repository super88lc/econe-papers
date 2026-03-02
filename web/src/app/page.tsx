'use client';

import { useState, useEffect, useCallback } from 'react';
import Header from '@/components/Header';
import DaySection from '@/components/DaySection';
import Footer from '@/components/Footer';
import PaperCard from '@/components/PaperCard';
import { DayPapers, Paper, Category } from '@/types';

export default function Home() {
  const [category, setCategory] = useState<Category>('All');
  const [selectedTag, setSelectedTag] = useState('All Tags');
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
  
  useEffect(() => {
    if (selectedTag !== 'All Tags') {
      // Collect all papers with selected tag
      const papers: Paper[] = [];
      days.forEach(day => {
        day.papers.forEach(paper => {
          const tags = paper.tags || [];
          if (tags.includes(selectedTag)) {
            papers.push(paper);
          }
        });
      });
      // Sort by score
      papers.sort((a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0));
      setCategoryPapers(papers);
      setShowTagView(true);
    } else {
      setShowTagView(false);
      setCategoryPapers([]);
    }
  }, [selectedTag, days]);
  
  const [categoryPapers, setCategoryPapers] = useState<Paper[]>([]);
  const [showCategoryView, setShowCategoryView] = useState(false);
  const [showTagView, setShowTagView] = useState(false);
  
  useEffect(() => {
    if (category === 'All') {
      setShowCategoryView(false);
      setCategoryPapers([]);
      setShowTagView(false);
    } else {
      const papers: Paper[] = [];
      days.forEach(day => {
        day.papers.forEach(paper => {
          if (paper.researchField.includes(category)) {
            papers.push(paper);
          }
        });
      });
      papers.sort((a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0));
      setCategoryPapers(papers);
      setShowCategoryView(true);
      setShowTagView(false);
    }
  }, [category, days]);
  
  useEffect(() => {
    if (showCategoryView || showTagView) return;
    
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
  }, [loadMore, showCategoryView, showTagView]);
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header 
        selectedCategory={category} 
        onCategoryChange={setCategory}
        selectedTag={selectedTag}
        onTagChange={setSelectedTag}
      />
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
        {showCategoryView ? (
          <section>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200"></div>
              <h2 className="text-sm font-medium text-gray-500">
                📂 {category} ({categoryPapers.length} papers)
              </h2>
              <div className="h-px flex-1 bg-gray-200"></div>
            </div>
            
            {categoryPapers.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                No papers in this category
              </div>
            )Papers.map((paper : (
              category, idx) => (
                <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
              ))
            )}
          </section>
        ) : showTagView ? (
          <section>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200"></div>
              <h2 className="text-sm font-medium text-gray-500">
                🏷️ {selectedTag} ({categoryPapers.length} papers)
              </h2>
              <div className="h-px flex-1 bg-gray-200"></div>
            </div>
            
            {categoryPapers.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                No papers with this tag
              </div>
            ) : (
              categoryPapers.map((paper, idx) => (
                <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
              ))
            )}
          </section>
        ) : (
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
                Loading...
              </div>
            )}
            
            {!hasMore && days.length > 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">
                End of content
              </div>
            )}
          </>
        )}
      </main>
      
      <Footer />
    </div>
  );
}
