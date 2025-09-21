'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Avatar } from '@/components/ui/avatar'
import { Message } from '@/types/chat'
import { formatDistanceToNow } from 'date-fns'

interface MessageItemProps {
  message: Message
}

export const MessageItem = ({ message }: MessageItemProps) => {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <Avatar
        size="sm"
        fallback={isUser ? 'U' : 'AI'}
        src={isUser ? undefined : '/icons/bot-avatar.png'}
      />
      
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : ''}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
          </span>
        </div>
        
        <div
          className={`rounded-2xl px-4 py-2 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
          }`}
        >
          {isAssistant ? (
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                code: ({ children, className }) => {
                  const isInline = !className
                  return isInline ? (
                    <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded text-sm">
                      {children}
                    </code>
                  ) : (
                    <pre className="bg-gray-200 dark:bg-gray-700 p-3 rounded-lg overflow-x-auto my-2">
                      <code className="text-sm">{children}</code>
                    </pre>
                  )
                },
                ul: ({ children }) => (
                  <ul className="list-disc pl-4 mb-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-4 mb-2">{children}</ol>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic my-2">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
        
        {message.error && (
          <div className="mt-1 text-xs text-red-500 dark:text-red-400">
            Failed to send message
          </div>
        )}
      </div>
    </div>
  )
}
