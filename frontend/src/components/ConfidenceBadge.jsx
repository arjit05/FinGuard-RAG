const COLOR_MAP = {
  HIGH: 'bg-green-100 text-green-800 border-green-300',
  MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300',
  LOW: 'bg-red-100 text-red-800 border-red-300',
  UNSURE: 'bg-slate-100 text-slate-600 border-slate-300',
}

export default function ConfidenceBadge({ confidence }) {
  const level = (confidence || 'UNSURE').toUpperCase()
  const cls = COLOR_MAP[level] || COLOR_MAP.UNSURE
  return (
    <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {level}
    </span>
  )
}
