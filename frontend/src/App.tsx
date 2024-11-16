import { useState } from 'react'
import GiftCardGenerator from './pages/GiftCardGenerator'
import OccasionQuestions from './pages/OccasionQuestions'

function App() {
  const [currentPage, setCurrentPage] = useState('generator')
  const [message, setMessage] = useState('')

  const handleGenerateCard = (message: string) => {
    setMessage(message)
    setCurrentPage('questions')
  }

  return (
    <>
      {currentPage === 'generator' && (
        <GiftCardGenerator onSubmit={handleGenerateCard} />
      )}
      {currentPage === 'questions' && (
        <OccasionQuestions initialMessage={message} />
      )}
    </>
  )
}

export default App
