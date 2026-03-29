import { clsx } from 'clsx'

const variants = {
  pending: 'bg-gray-100 text-gray-700',
  processing: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  refunded: 'bg-purple-100 text-purple-700',
  success: 'bg-green-100 text-green-700',
  test: 'bg-amber-100 text-amber-700',
  live: 'bg-green-100 text-green-700',
}

interface BadgeProps {
  status: keyof typeof variants
  label?: string
}

export default function Badge({ status, label }: BadgeProps) {
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', variants[status])}>
      {label || status}
    </span>
  )
}
