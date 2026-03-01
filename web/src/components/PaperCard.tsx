'use client';

import { useState } from 'react';
import { Paper } from '@/types';

interface PaperCardProps {
  paper: Paper;
}

function StarRating({ rating }: { rating: number }) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);
  
  return (
    <span className="text-[#d4a574]">
      {'★'.repeat(fullStars)}
      {hasHalf && '☆'}
      {'☆'.repeat(emptyStars)}
    </span>
  );
}

export default function PaperCard({ paper }: PaperCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 mb-3 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg font-bold text-[#d4a574]">
              ★ {paper.scores.overall.toFixed(1)}
            </span>
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              {paper.researchField}
            </span>
          </div>
          
          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {paper.chineseTitle}
          </h3>
          
          <p className="text-sm text-gray-500 mb-2">
            {paper.authors.join(', ')}
          </p>
          
          {!expanded && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {paper.summary}
            </p>
          )}
        </div>
      </div>
      
      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-sm text-gray-700 mb-3">
            {paper.chineseAbstract}
          </p>
          
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            <span>
              选题新颖度: <StarRating rating={paper.scores.novelty} />
            </span>
            <span>
              研究水平: <StarRating rating={paper.scores.quality} />
            </span>
            <span>
              可读性: <StarRating rating={paper.scores.readability} />
            </span>
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
              href={`https://arxiv.org/abs/${paper.id}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition-colors"
            >
              arXiv
            </a>
          </div>
          
          <div className="flex gap-2 mt-2 flex-wrap">
            {paper.keywords.map((keyword) => (
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
