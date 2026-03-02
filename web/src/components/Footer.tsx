export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-gray-50 py-6 mt-8">
      <div className="max-w-4xl mx-auto px-4 text-center text-sm text-gray-500">
        <p>
          Powered by AI | Data Source: <a 
            href="https://arxiv.org" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-[#1e3a5f] hover:underline"
          >
            arXiv.org
          </a>
        </p>
        <p className="mt-1">
          Daily auto-fetched + AI analysis
        </p>
      </div>
    </footer>
  );
}
