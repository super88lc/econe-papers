import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const date = searchParams.get('date');
  const before = searchParams.get('before');
  const limit = parseInt(searchParams.get('limit') || '30');
  
  try {
    const dataPath = path.join(process.cwd(), 'src/lib/data.json');
    const fileContent = fs.readFileSync(dataPath, 'utf-8');
    const data = JSON.parse(fileContent);
    
    let days = data.days || [];
    
    // Filter by specific date
    if (date) {
      days = days.filter((d: any) => d.date === date);
    }
    
    // Filter by date range (before date)
    if (before) {
      days = days.filter((d: any) => d.date < before).slice(0, limit);
    }
    
    // Sort by date descending
    days.sort((a: any, b: any) => b.date.localeCompare(a.date));
    
    return NextResponse.json({
      days,
      lastUpdated: data.lastUpdated,
      total: days.reduce((acc: number, d: any) => acc + d.papers.length, 0)
    });
  } catch (error) {
    console.error('Error loading papers:', error);
    return NextResponse.json({
      days: [],
      lastUpdated: new Date().toISOString(),
      total: 0
    });
  }
}
