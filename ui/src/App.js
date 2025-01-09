import React, { useState } from 'react';
import './App.css';

function App() {
  // Step 1: State to store the input value
  const [inputValue, setInputValue] = useState('');
  const [responseData, setResponseData] = useState(null); // To store API response
  const [loading, setLoading] = useState(false); // To handle loading state
  const [error, setError] = useState(null); // To handle errors

  // Step 2: Handle the button click and make the API call
  const handleButtonClick = async () => {
    // URL encode the userId
    const encodedUserId = encodeURIComponent(inputValue);

    // Step 3: Make the API call
    setLoading(true); // Start loading

    try {
      const response = await fetch(`https://wz3soxp4h1.execute-api.us-east-1.amazonaws.com/dev/user-playlist?userId=${encodedUserId}`);
      
      if (!response.ok) {
        throw new Error('API call failed');
      }

      const data = await response.json();
      setResponseData(data); // Store the API response
    } catch (error) {
      setError('There was an error fetching the data.');
    } finally {
      setLoading(false); // Stop loading
    }
  };

  return (
    <div className="App">
      <h1>User Playlist API</h1>

      {/* Step 4: Text input */}
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)} // Update state on input change
        placeholder="Enter userId"
      />

      {/* Step 5: Go button */}
      <button onClick={handleButtonClick}>Go</button>

      {/* Step 6: Display loading message */}
      {loading && <p>Loading...</p>}

      {/* Step 7: Display API response */}
      {responseData && (
        <div>
          <h3>API Response:</h3>
          <pre>{JSON.stringify(responseData, null, 2)}</pre>
        </div>
      )}

      {/* Step 8: Display error message */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;
