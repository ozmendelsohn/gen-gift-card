'use client'

import { useState } from 'react'
import { Button } from "../components/ui/button"
import { Textarea } from "../components/ui/textarea"

interface GiftCardGeneratorProps {
  onSubmit: (message: string) => void
}

export default function GiftCardGenerator({ onSubmit }: GiftCardGeneratorProps) {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() === '') {
      setError('Please enter a message for your gift card.')
      return
    }
    setError('')
    onSubmit(message)
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-rose-100 to-teal-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">Create Your Gift Card</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
              Enter your gift card message:
            </label>
            <Textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Write your heartfelt message here..."
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 text-gray-900 placeholder:text-gray-500"
              rows={5}
            />
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </div>
          <Button type="submit" className="w-full bg-teal-500 hover:bg-teal-600 text-white font-bold py-2 px-4 rounded transition duration-300">
            Generate Gift Card
          </Button>
        </form>
      </div>
    </div>
  )
}