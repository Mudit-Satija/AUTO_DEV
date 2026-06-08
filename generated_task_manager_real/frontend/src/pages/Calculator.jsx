import React, { useState } from 'react'
import api from '../services/api'

const Calculator = () => {
  const [input, setInput] = useState('')
  const [result, setResult] = useState('')

  const handleCalculate = async () => {
    try {
      const response = await api.post('/calculator/evaluate', { expression: input })
      setResult(response.data.result)
    } catch (error) {
      setResult('Error')
    }
  }

  const handleClear = () => {
    setInput('')
    setResult('')
  }

  const handleButtonClick = (value) => {
    setInput((prev) => prev + value)
  }

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto', fontFamily: 'Arial' }}>
      <h1>Calculator</h1>
      <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px', textAlign: 'right', backgroundColor: '#f9f9f9' }}>
        {input}
      </div>
      <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px', textAlign: 'right', backgroundColor: '#f9f9f9' }}>
        {result}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        <button onClick={handleClear} style={{ padding: '10px', fontSize: '18px' }}>C</button>
        <button onClick={() => handleButtonClick('(')} style={{ padding: '10px', fontSize: '18px' }}>(</button>
        <button onClick={() => handleButtonClick(')')} style={{ padding: '10px', fontSize: '18px' }}>)</button>
        <button onClick={() => handleButtonClick('/')} style={{ padding: '10px', fontSize: '18px' }}>/</button>
        <button onClick={() => handleButtonClick('7')} style={{ padding: '10px', fontSize: '18px' }}>7</button>
        <button onClick={() => handleButtonClick('8')} style={{ padding: '10px', fontSize: '18px' }}>8</button>
        <button onClick={() => handleButtonClick('9')} style={{ padding: '10px', fontSize: '18px' }}>9</button>
        <button onClick={() => handleButtonClick('*')} style={{ padding: '10px', fontSize: '18px' }}>*</button>
        <button onClick={() => handleButtonClick('4')} style={{ padding: '10px', fontSize: '18px' }}>4</button>
        <button onClick={() => handleButtonClick('5')} style={{ padding: '10px', fontSize: '18px' }}>5</button>
        <button onClick={() => handleButtonClick('6')} style={{ padding: '10px', fontSize: '18px' }}>6</button>
        <button onClick={() => handleButtonClick('-')} style={{ padding: '10px', fontSize: '18px' }}>-</button>
        <button onClick={() => handleButtonClick('1')} style={{ padding: '10px', fontSize: '18px' }}>1</button>
        <button onClick={() => handleButtonClick('2')} style={{ padding: '10px', fontSize: '18px' }}>2</button>
        <button onClick={() => handleButtonClick('3')} style={{ padding: '10px', fontSize: '18px' }}>3</button>
        <button onClick={() => handleButtonClick('+')} style={{ padding: '10px', fontSize: '18px' }}>+</button>
        <button onClick={() => handleButtonClick('0')} style={{ padding: '10px', fontSize: '18px' }}>0</button>
        <button onClick={() => handleButtonClick('.')} style={{ padding: '10px', fontSize: '18px' }}>.</button>
        <button onClick={handleCalculate} style={{ padding: '10px', fontSize: '18px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px' }}>=</button>
      </div>
    </div>
  )
}

export default Calculator