'use client';

import { useState, useEffect } from 'react';
import { Paper } from '@/types';

interface PaperCardProps {
  paper: Paper;
}

function StarRating({ rating, onRate, readonly = false }: { rating: number; onRate?: (r: number) => void; readonly?: boolean }) {
  const [hoverRating, setHoverRating] = useState(0);
  
  return (
    <span className={readonly ? "" : "cursor-pointer"}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`text-lg ${
            star <= (hoverRating || rating) ? 'text-yellow-400' : 'text-gray-300'
          } ${!readonly ? 'hover:text-yellow-400' : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            if (!readonly && onRate) onRate(star);
          }}
          onMouseEnter={() => !readonly && setHoverRating(star)}
          onMouseLeave={() => !readonly && setHoverRating(0)}
        >
          ★
        </span>
      ))}
    </span>
  );
}

export default function PaperCard({ paper }: PaperCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [userRating, setUserRating] = useState(0);
  
  useEffect(() => {
    const ratings = JSON.parse(localStorage.getItem('paperRatings') || '{}');
    const paperId = paper.id.replace('http://arxiv.org/abs/', '');
    setUserRating(ratings[paperId] || 0);
  }, [paper.id]);
  
  const handleRate = (rating: number) => {
    const ratings = JSON.parse(localStorage.getItem('paperRatings') || '{}');
    const paperId = paper.id.replace('http://arxiv.org/abs/', '');
    ratings[paperId] = rating;
    localStorage.setItem('paperRatings', JSON.stringify(ratings));
    setUserRating(rating);
  };
  
  const paperId = paper.id.replace('http://arxiv.org/abs/', '');
  const tags = paper.tags || [];
  
  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 mb-3 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-lg font-bold text-[#d4a574]">
              ★ {paper.scores.overall.toFixed(1)}
            </span>
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              {paper.researchField}
            </span>
            {tags.slice(0, 2).map((tag: string) => (
              <span key={tag} className="px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded border border-green-200">
                {tag}
              </span>
            ))}
          </div>
          
          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {paper.title}
          </h3>
          
          <p className="text-sm text-gray-500 mb-2">
            {paper.authors.join(', ')}
          </p>
          
          {!expanded && (
            <p className="text-sm text-gray-600 line-clamp-3">
              {paper.abstract}
            </p>
          )}
        </div>
      </div>
      
      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-sm text-gray-700 mb-3">
            {paper.abstract}
          </p>
          
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            <span>
              Novelty: <StarRating rating={paper.scores.novelty} readonly />
            </span>
            <span>
              Quality: <StarRating rating={paper.scores.quality} readonly />
            </span>
            <span>
              Readability: <StarRating rating={paper.scores.readability} readonly />
            </span>
          </div>
          
          {/* User rating */}
          <div className="flex items-center gap-3 mb-3 p-2 bg-yellow-50 rounded-lg">
            <span className="text-sm text-gray-600">Your Rating:</span>
            <StarRating rating={userRating} onRate={handleRate} />
            {userRating > 0 && (
              <span className="text-xs text-green-600">✓ Saved</span>
            )}
          </div>
          
          <div className="flex gap-2">
            <a
              href={paper.pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-3 py-1.5 bg-[#1e3a5f] text-white text-sm rounded hover:bg-[#2a4a73] transition-colors"
            >
              PDF
            </a>
            <a
              href={`https://arxiv.org/abs/${paperId}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition-colors"
            >
              arXiv
            </a>
          </div>
          
          <div className="flex gap-2 mt-2 flex-wrap">
            {tags.map((keyword: string) => (
              <span 
                key={keyword}
                className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded"
              >
                #{keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
