"use client";
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Search, FileText, MessageSquare, Loader2, CheckCircle, XCircle, Database, Send } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export default function DocuMind() {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    
    for (const file of files) {
      setUploading(true);
      setUploadStatus({ type: 'loading', message: `Uploading ${file.name}...` });

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          setUploadedFiles(prev => [...prev, result]);
          setUploadStatus({ 
            type: 'success', 
            message: `✓ ${file.name} processed into ${result.chunks_created} chunks` 
          });
          fetchStats();
        } else {
          setUploadStatus({ 
            type: 'error', 
            message: `✗ Error: ${result.detail}` 
          });
        }
      } catch (error) {
        setUploadStatus({ 
          type: 'error', 
          message: `✗ Upload failed: ${error.message}` 
        });
      }

      setUploading(false);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSearchSubmit = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchResults([]);

    try {
      const response = await fetch(`${API_BASE_URL}/search/semantic`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, top_k: 5 }),
      });

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    }

    setSearching(false);
  };

  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  const handleAskSubmit = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/search/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: chatInput, 
          top_k: 5,
          conversation_history: chatMessages.slice(-6)
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const assistantMessage = {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
        };
        setChatMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          role: 'assistant',
          content: `Error: ${data.detail || 'Failed to get response'}`,
          isError: true
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        isError: true
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }

    setChatLoading(false);
  };

  const handleChatKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <FileText className="w-12 h-12 text-purple-400" />
            DocuMind
          </h1>
          <p className="text-purple-200 text-lg">AI-Powered Technical Documentation Assistant</p>
          {stats && (
            <div className="mt-4 inline-flex items-center gap-2 bg-purple-800/30 px-4 py-2 rounded-full text-purple-200">
              <Database className="w-4 h-4" />
              <span>{stats.total_chunks} chunks indexed</span>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-slate-800/50 p-1 rounded-lg backdrop-blur-sm">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-3 px-4 rounded-md font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'upload'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Upload className="w-5 h-5" />
            Upload Documents
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`flex-1 py-3 px-4 rounded-md font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'search'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Search className="w-5 h-5" />
            Search
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-3 px-4 rounded-md font-medium transition-all flex items-center justify-center gap-2 ${
              activeTab === 'chat'
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <MessageSquare className="w-5 h-5" />
            Ask Questions
          </button>
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-slate-700">
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-purple-400/50 rounded-lg p-12 text-center cursor-pointer hover:border-purple-400 hover:bg-purple-900/20 transition-all"
            >
              <Upload className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <p className="text-xl text-white mb-2">Drop files here or click to upload</p>
              <p className="text-slate-400">Supports: .md, .txt, .pdf, .py, .js, .ts, .java</p>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                multiple
                className="hidden"
                accept=".md,.txt,.pdf,.py,.js,.ts,.tsx,.jsx,.java,.go,.rs,.cpp,.c,.h"
              />
            </div>

            {uploadStatus && (
              <div className={`mt-6 p-4 rounded-lg flex items-center gap-3 ${
                uploadStatus.type === 'success' ? 'bg-green-900/30 border border-green-500/50' :
                uploadStatus.type === 'error' ? 'bg-red-900/30 border border-red-500/50' :
                'bg-blue-900/30 border border-blue-500/50'
              }`}>
                {uploadStatus.type === 'success' && <CheckCircle className="w-5 h-5 text-green-400" />}
                {uploadStatus.type === 'error' && <XCircle className="w-5 h-5 text-red-400" />}
                {uploadStatus.type === 'loading' && <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />}
                <span className="text-white">{uploadStatus.message}</span>
              </div>
            )}

            {uploadedFiles.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-white mb-4">Recently Uploaded</h3>
                <div className="space-y-2">
                  {uploadedFiles.slice(-5).reverse().map((file, idx) => (
                    <div key={idx} className="bg-slate-700/50 p-4 rounded-lg flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-purple-400" />
                        <div>
                          <p className="text-white font-medium">{file.filename}</p>
                          <p className="text-sm text-slate-400">{file.chunks_created} chunks • {(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                      <span className="text-xs text-purple-300 bg-purple-900/30 px-3 py-1 rounded-full">
                        {file.file_type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-slate-700">
            <div className="mb-6">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  placeholder="Search your documentation..."
                  className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={handleSearchSubmit}
                  disabled={searching}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {searching ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  Search
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {searchResults.map((result, idx) => (
                <div key={idx} className="bg-slate-700/50 p-5 rounded-lg border border-slate-600 hover:border-purple-500/50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-purple-400" />
                      <span className="text-white font-medium">{result.filename}</span>
                      <span className="text-xs text-slate-400">Chunk {result.chunk_index}</span>
                    </div>
                    <span className="text-xs text-purple-300 bg-purple-900/30 px-2 py-1 rounded">
                      {(result.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">{result.text_preview}</p>
                </div>
              ))}
              {searchResults.length === 0 && searchQuery && !searching && (
                <p className="text-center text-slate-400 py-8">No results found. Try a different query.</p>
              )}
            </div>
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 flex flex-col" style={{ height: '600px' }}>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {chatMessages.length === 0 && (
                <div className="text-center py-12">
                  <MessageSquare className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                  <p className="text-white text-lg mb-2">Ask anything about your documentation</p>
                  <p className="text-slate-400">I'll search and provide answers with citations</p>
                </div>
              )}
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl ${msg.role === 'user' ? 'bg-purple-600' : msg.isError ? 'bg-red-900/30 border border-red-500/50' : 'bg-slate-700'} rounded-lg p-4`}>
                    <p className="text-white whitespace-pre-wrap">{msg.content}</p>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-600">
                        <p className="text-xs text-slate-300 mb-2">Sources:</p>
                        {msg.sources.map((source, sidx) => (
                          <div key={sidx} className="text-xs text-slate-400 mb-1">
                            • {source.filename} (chunk {source.chunk_index})
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-700 rounded-lg p-4">
                    <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-slate-700">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={handleChatKeyPress}
                  placeholder="Ask a question about your docs..."
                  className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={chatLoading}
                />
                <button
                  onClick={handleAskSubmit}
                  disabled={chatLoading || !chatInput.trim()}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {chatLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}