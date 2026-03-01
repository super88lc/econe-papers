'use client';

import { Category, CATEGORIES } from '@/types';

interface HeaderProps {
  selectedCategory: Category;
  onCategoryChange: (category: Category) => void;
}

export default function Header({ selectedCategory, onCategoryChange }: HeaderProps) {
  const today = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-[#1e3a5f]">
            Econe Papers
          </h1>
          <span className="text-sm text-gray-500">
            今日更新: {today}
          </span>
        </div>
        
        <nav className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {CATEGORIES.map((category) => (
            <button
              key={category}
              onClick={() => onCategoryChange(category)}
              className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-[#1e3a5f] text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {category}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}
