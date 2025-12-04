import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('Загрузка...')
  const [health, setHealth] = useState('Проверка...')

  useEffect(() => {
    // Проверка бэкенда
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(() => setMessage('Ошибка подключения к бэкенду'))

    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('Ошибка'))
  }, [])

  return (
    <div className="App">
      <h1>Hack.ITAM.Misis 🚀</h1>
      <div className="card">
        <p>Бэкенд: {message}</p>
        <p>Статус: {health}</p>
      </div>
      <p className="read-the-docs">
        Готовы к хакатону!
      </p>
    </div>
  )
}

export default App