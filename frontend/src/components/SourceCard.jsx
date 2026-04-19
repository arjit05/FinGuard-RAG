import { useState } from 'react'

export default function SourceCard({ source, retrievalScore }) {
  const [copied, setCopied] = useState(false)

  if (!source || source === 'N/A') return null

  const handleCopy = () => {
    navigator.clipboard.writeText(source)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="mt-2 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 text-blue-700 font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="break-all">{source}</span>
        </div>
        <button
          onClick={handleCopy}
          className="shrink-0 text-xs text-blue-500 hover:text-blue-700 underline"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      {retrievalScore != null && (
        <div className="mt-1 text-xs text-blue-500">
          Retrieval score: {retrievalScore.toFixed(3)}
        </div>
      )}
    </div>
  )
}
