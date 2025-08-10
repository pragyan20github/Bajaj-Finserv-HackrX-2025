import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ChatWindow = ({ currentChat, setCurrentChat, startNewChat }) => {
    const [pdfUrl, setPdfUrl] = useState('');
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const API_URL_ENDPOINT = import.meta.env.VITE_REACT_APP_API_URL_ENDPOINT;
    const API_KEY = import.meta.env.VITE_REACT_APP_HACKATHON_API_KEY;

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate the form inputs
        if (!pdfUrl) {
            alert("Please enter a PDF URL.");
            return;
        }
        if (!question.trim()) {
            alert("Please enter a question before sending.");
            return;
        }

        setIsLoading(true);

        const endpoint = API_URL_ENDPOINT;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`,
        };
        const body = JSON.stringify({
            documents: pdfUrl,
            questions: [question],
        });

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers,
                body,
            });

            if (!response.ok) {
                throw new Error('Failed to fetch response from backend.');
            }

            const data = await response.json();
            const newAnswer = data.answers[0];
            const chatMessage = { sender: 'user', text: question };
            const botMessage = { sender: 'bot', text: newAnswer };
            
            setCurrentChat(prevChat => ({
                id: prevChat ? prevChat.id : uuidv4(),
                messages: [...(prevChat?.messages || []), chatMessage, botMessage],
                pdfIdentifier: prevChat?.pdfIdentifier || pdfUrl,
            }));

            setQuestion('');
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setIsLoading(false);
        }
    };
    
    const chatInProgress = currentChat && currentChat.messages.length > 0;

    return (
        <div className="chat-window">
            <div className="header">
                <button onClick={startNewChat} className="new-chat-btn">
                    + New Chat
                </button>
            </div>
            <div className="messages">
                {currentChat && currentChat.messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        {msg.text}
                    </div>
                ))}
                {isLoading && <div className="message bot">Loading...</div>}
            </div>
            
            <form onSubmit={handleSubmit} className="input-form">
                <input
                    type="text"
                    placeholder="Enter PDF URL..."
                    value={pdfUrl}
                    onChange={(e) => setPdfUrl(e.target.value)}
                    disabled={chatInProgress}
                />
                <input
                    type="text"
                    placeholder="Ask a question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                />
                <button type="submit" disabled={isLoading}>Send</button>
            </form>
        </div>
    );
};

export default ChatWindow;