'use client'

import { useAuth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'
import { ChatContainer } from '@/components/chat/chat-container'
import { useEffect } from 'react'

export default function ChatPage() {
  const { isLoaded, userId } = useAuth()

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (isLoaded && !userId) {
      redirect('/')
    }
  }, [isLoaded, userId])

  if (!isLoaded) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-blue-950 to-purple-950">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!userId) {
    return null // Will redirect
  }

  return (
    <div className="h-screen bg-gradient-to-br from-gray-950 via-blue-950 to-purple-950">
      <ChatContainer />
    </div>
  )
}
