import ConfidenceBadge from './ConfidenceBadge'
import SourceCard from './SourceCard'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-2.5 text-white shadow-sm">
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        </div>
      </div>
    )
  }

  const { answer, source, confidence, retrieval_score, guardrails_passed, failed_rules, error } = message.data || {}

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm border border-slate-200">
        {error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : (
          <>
            <p className="whitespace-pre-wrap text-sm text-slate-800">{answer}</p>
            <div className="mt-2 flex items-center gap-2 flex-wrap">
              <ConfidenceBadge confidence={confidence} />
              {!guardrails_passed && failed_rules?.length > 0 && (
                <span className="text-xs text-red-500 border border-red-200 bg-red-50 px-2 py-0.5 rounded-full">
                  Guardrail: {failed_rules.join(', ')}
                </span>
              )}
            </div>
            <SourceCard source={source} retrievalScore={retrieval_score} />
          </>
        )}
      </div>
    </div>
  )
}
