'use client';

import { Category } from '@/types';

const CATEGORIES = ['全部', '金融', '计量', '理论', '宏观', '微观', '行为', '产业', '环境', '劳动', '其他'];

const TAGS = [
  '全部标签',
  '博弈论',
  '数字经济', 
  '平台经济',
  '技术经济',
  '行为经济学',
  '计量+ML',
  '实验经济学',
  '劳动经济学',
  '环境经济学',
  '金融科技'
];

interface HeaderProps {
  selectedCategory: Category;
  onCategoryChange: (category: Category) => void;
  selectedTag?: string;
  onTagChange?: (tag: string) => void;
}

export default function Header({ selectedCategory, onCategoryChange, selectedTag = '全部标签', onTagChange }: HeaderProps) {
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
        
        <div className="mb-3">
          <div className="text-xs text-gray-500 mb-1">分类</div>
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {CATEGORIES.map((category) => (
              <button
                key={category}
                onClick={() => onCategoryChange(category as Category)}
                className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                  selectedCategory === category
                    ? 'bg-[#1e3a5f] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
        
        {onTagChange && (
          <div>
            <div className="text-xs text-gray-500 mb-1">标签</div>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {TAGS.map((tag) => (
                <button
                  key={tag}
                  onClick={() => onTagChange(tag)}
                  className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                    selectedTag === tag
                      ? 'bg-[#d4a574] text-white'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
