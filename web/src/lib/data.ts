import { Paper, DayPapers } from '@/types';

export const MOCK_PAPERS: Paper[] = [
  {
    id: '2502.12345',
    title: 'Machine Learning for Causal Inference in Economics: A Review of Recent Advances',
    authors: ['Zhang Wei', 'Li Ming', 'Wang Fang'],
    abstract: 'This paper reviews recent advances in machine learning methods for causal inference in economics...',
    categories: ['q-fin.EC', 'stat.ML'],
    published: '2026-02-28',
    updated: '2026-02-28',
    pdfUrl: 'https://arxiv.org/pdf/2502.12345',
    chineseTitle: '经济学因果推断中的机器学习：最新进展综述',
    chineseAbstract: '本文综述了因果推断在经济学中的机器学习方法的最新进展...',
    researchField: '计量经济学',
    keywords: ['machine-learning', 'causal-inference', 'econometrics'],
    scores: {
      overall: 9.2,
      novelty: 5,
      quality: 5,
      readability: 4
    },
    summary: '本文系统综述了机器学习在因果推断中的应用，为经济学研究者提供了方法论指南。'
  },
  {
    id: '2502.12344',
    title: 'Behavioral Economics and Climate Policy: Experimental Evidence',
    authors: ['Chen Jinping', 'Liu Yang'],
    abstract: 'We conduct a series of experiments to understand how behavioral factors affect climate policy compliance...',
    categories: ['q-fin.EC', 'econ.GN'],
    published: '2026-02-28',
    updated: '2026-02-28',
    pdfUrl: 'https://arxiv.org/pdf/2502.12344',
    chineseTitle: '行为经济学与气候政策：实验证据',
    chineseAbstract: '我们进行了一系列实验来理解行为因素如何影响气候政策的遵守...',
    researchField: '行为经济学',
    keywords: ['behavioral-economics', 'climate-policy', 'experiments'],
    scores: {
      overall: 8.8,
      novelty: 5,
      quality: 4,
      readability: 5
    },
    summary: '通过实验方法研究了行为经济学因素对气候政策效果的影响。'
  },
  {
    id: '2502.12343',
    title: 'Monetary Policy in a Post-Pandemic World: New Challenges',
    authors: ['Zhou Xiaoming', 'Huang Jing'],
    abstract: 'The post-pandemic economic environment presents new challenges for monetary policy...',
    categories: ['q-fin.EC', 'econ.GN'],
    published: '2026-02-27',
    updated: '2026-02-27',
    pdfUrl: 'https://arxiv.org/pdf/2502.12343',
    chineseTitle: '后疫情时代的货币政策：新挑战',
    chineseAbstract: '后疫情经济环境给货币政策带来了新的挑战...',
    researchField: '宏观经济学',
    keywords: ['monetary-policy', 'post-pandemic', 'macro-economics'],
    scores: {
      overall: 8.5,
      novelty: 4,
      quality: 5,
      readability: 4
    },
    summary: '分析了后疫情时代货币政策面临的新挑战和应对策略。'
  },
  {
    id: '2502.12342',
    title: 'High-Frequency Trading and Market Microstructure: New Evidence from Crypto Markets',
    authors: ['Wu Lei', 'Zhao Qian'],
    abstract: 'This paper examines the relationship between high-frequency trading and market quality...',
    categories: ['q-fin.TR', 'q-fin.MF'],
    published: '2026-02-27',
    updated: '2026-02-27',
    pdfUrl: 'https://arxiv.org/pdf/2502.12342',
    chineseTitle: '高频交易与市场微观结构：来自加密市场的新证据',
    chineseAbstract: '本文研究了高频交易与市场质量之间的关系...',
    researchField: '金融经济学',
    keywords: ['high-frequency-trading', 'market-microstructure', 'crypto'],
    scores: {
      overall: 8.3,
      novelty: 4,
      quality: 4,
      readability: 5
    },
    summary: '研究了加密市场中高频交易对市场微观结构的影响。'
  },
  {
    id: '2502.12341',
    title: 'Industrial Organization and Digital Platforms: Competition Policy Implications',
    authors: ['Sun Cheng', 'Ma Lin'],
    abstract: 'Digital platforms have transformed competition in many industries...',
    categories: ['q-fin.EC', 'econ.GN'],
    published: '2026-02-26',
    updated: '2026-02-26',
    pdfUrl: 'https://arxiv.org/pdf/2502.12341',
    chineseTitle: '产业组织与数字平台：竞争政策含义',
    chineseAbstract: '数字平台改变了许多行业的竞争格局...',
    researchField: '产业经济学',
    keywords: ['industrial-organization', 'digital-platforms', 'competition-policy'],
    scores: {
      overall: 8.0,
      novelty: 4,
      quality: 4,
      readability: 4
    },
    summary: '分析了数字平台对产业组织结构和竞争政策的影响。'
  }
];

export const MOCK_DAY_PAPERS: DayPapers[] = [
  {
    date: '2026-03-01',
    papers: MOCK_PAPERS,
    total: 10
  },
  {
    date: '2026-02-28',
    papers: MOCK_PAPERS.slice(0, 8),
    total: 8
  },
  {
    date: '2026-02-27',
    papers: MOCK_PAPERS.slice(0, 10),
    total: 10
  },
  {
    date: '2026-02-26',
    papers: MOCK_PAPERS.slice(0, 6),
    total: 6
  },
  {
    date: '2026-02-25',
    papers: MOCK_PAPERS.slice(0, 10),
    total: 10
  }
];
