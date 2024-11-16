'use client'

import { useState } from 'react'
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group"
import { Textarea } from "../components/ui/textarea"

type Question = {
  question: string;
  placeholder: string | null;
}

type OccasionQuestions = {
  [key: string]: {
    questions: Question[];
  };
}

const occasionQuestions: OccasionQuestions = {
  birthday: {
    questions: [
      { question: "What is your relationship with the recipient? (e.g., Friend, Colleague)", placeholder: null },
      { question: "What are the recipient's hobbies or interests? (e.g., Reading, Sports)", placeholder: "Surprise me" },
      { question: "Share a funny or memorable story about the recipient. (e.g., A vacation mishap)", placeholder: "Surprise me" },
      { question: "What is a trait or talent of the recipient you admire? (e.g., Creativity, kindness)", placeholder: "Surprise me" },
    ],
  },
  wedding: {
    questions: [
      { question: "How do you know the couple? (e.g., College friends, Neighbors)", placeholder: null },
      { question: "What is a cherished memory you have with the couple? (e.g., A group trip)", placeholder: "Surprise me" },
      { question: "Offer a piece of advice or a wish for their future. (e.g., Always listen to each other)", placeholder: "Surprise me" },
      { question: "Choose a theme that represents the couple's relationship. (e.g., Adventure, romance)", placeholder: "Surprise me" },
    ],
  },
  graduation: {
    questions: [
      { question: "What is your relationship with the graduate? (e.g., Aunt, Mentor)", placeholder: null },
      { question: "What are the graduate's future aspirations? (e.g., Engineer, Artist)", placeholder: "Surprise me" },
      { question: "Share a memorable experience you had with the graduate. (e.g., Science fair)", placeholder: "Surprise me" },
      { question: "What qualities make the graduate unique? (e.g., Determination, intelligence)", placeholder: "Surprise me" },
    ],
  },
  retirement: {
    questions: [
      { question: "How have you known or worked with the retiree? (e.g., Co-worker, Long-time friend)", placeholder: null },
      { question: "What is a significant contribution or achievement of the retiree? (e.g., Project success)", placeholder: "Surprise me" },
      { question: "Share a humorous or heartwarming story about the retiree. (e.g., Office party event)", placeholder: "Surprise me" },
      { question: "What hobbies or activities do you think the retiree will enjoy? (e.g., Gardening, travel)", placeholder: "Surprise me" },
    ],
  },
  generic_occasion: {
    questions: [
      { question: "What is your relationship with the recipient? (e.g., Family member, Colleague)", placeholder: null },
      { question: "What kind of activities or hobbies does the recipient enjoy? (e.g., Cooking, Hiking)", placeholder: "Surprise me" },
      { question: "Share a memorable experience or moment you've had with the recipient. (e.g., A surprise party)", placeholder: "Surprise me" },
      { question: "What is the occasion or reason for the gift? (e.g., Birthday, Anniversary)", placeholder: "Surprise me" },
    ],
  },
}

interface OccasionQuestionsProps {
  initialMessage: string;
}

export default function OccasionQuestions({ initialMessage }: OccasionQuestionsProps) {
  const [selectedOccasion, setSelectedOccasion] = useState<string>('birthday')
  const [answers, setAnswers] = useState<{ [key: string]: string }>({})

  const handleAnswerChange = (index: number, value: string) => {
    setAnswers(prev => ({ ...prev, [index]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Selected Occasion:', selectedOccasion)
    console.log('Initial Message:', initialMessage)
    console.log('Answers:', answers)
    // TODO: Implement the next step (e.g., generating the gift card message)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-rose-100 to-teal-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">Gift Card Details</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <Label htmlFor="occasion" className="text-lg font-semibold">Select the occasion:</Label>
            <RadioGroup
              id="occasion"
              value={selectedOccasion}
              onValueChange={setSelectedOccasion}
              className="flex flex-wrap gap-4"
            >
              {Object.keys(occasionQuestions).map((occasion) => (
                <div key={occasion} className="flex items-center space-x-2">
                  <RadioGroupItem value={occasion} id={occasion} />
                  <Label htmlFor={occasion} className="capitalize">{occasion.replace('_', ' ')}</Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          {occasionQuestions[selectedOccasion].questions.map((q, index) => (
            <div key={index} className="space-y-2">
              <Label htmlFor={`question-${index}`} className="text-sm font-medium text-gray-700">
                {q.question}
              </Label>
              {index === 0 ? (
                <Input
                  id={`question-${index}`}
                  value={answers[index] || ''}
                  onChange={(e) => handleAnswerChange(index, e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  required
                />
              ) : (
                <Textarea
                  id={`question-${index}`}
                  value={answers[index] || ''}
                  onChange={(e) => handleAnswerChange(index, e.target.value)}
                  placeholder={q.placeholder || ''}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  rows={3}
                />
              )}
            </div>
          ))}

          <Button type="submit" className="w-full bg-teal-500 hover:bg-teal-600 text-white font-bold py-2 px-4 rounded transition duration-300">
            Generate Gift Card Message
          </Button>
        </form>
      </div>
    </div>
  )
} 