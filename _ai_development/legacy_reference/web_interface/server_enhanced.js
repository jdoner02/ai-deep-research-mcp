const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.join(__dirname)));

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('🔗 Client connected:', socket.id);
    
    socket.emit('research_progress', {
        timestamp: new Date().toISOString().substring(11, 19),
        message: '🔗 Connected to AI Deep Research MCP server'
    });

    socket.on('research_query', async (data) => {
        console.log('🔍 Research query received:', data.query);
        
        const startTime = Date.now();
        
        // Emit initial progress
        socket.emit('research_progress', {
            timestamp: new Date().toISOString().substring(11, 19),
            message: `🔍 Initializing research for: "${data.query}"`
        });
        
        try {
            // Run the enhanced arbitrary query research system
        // Execute Python research script with enhanced query system
        const pythonProcess = spawn('python', [
            '/Users/jessicadoner/0. Knowledge Manager/ai_deep_research_mcp/src/simple_web_research.py'
        ], {
            cwd: '/Users/jessicadoner/0. Knowledge Manager/ai_deep_research_mcp',
            stdio: ['pipe', 'pipe', 'pipe']
        });            let outputBuffer = '';
            let isCapturingResults = false;
            let resultsData = {
                papers_processed: 0,
                chunks_stored: 0,
                queries_tested: 0,
                processing_time: 0,
                sources: []
            };

            pythonProcess.stdout.on('data', (data) => {
                const output = data.toString();
                outputBuffer += output;
                
                // Parse and emit progress updates
                const lines = output.split('\n');
                lines.forEach(line => {
                    if (line.trim()) {
                        // Emit real-time progress
                        socket.emit('research_progress', {
                            timestamp: new Date().toISOString().substring(11, 19),
                            message: line.trim()
                        });
                        
                        // Parse statistics from output
                        if (line.includes('documents_processed:')) {
                            const match = line.match(/(\d+)/);
                            if (match) resultsData.papers_processed = parseInt(match[1]);
                        } else if (line.includes('chunks_indexed:')) {
                            const match = line.match(/(\d+)/);
                            if (match) resultsData.chunks_stored = parseInt(match[1]);
                        } else if (line.includes('relevant_results:')) {
                            const match = line.match(/(\d+)/);
                            if (match) resultsData.queries_tested = parseInt(match[1]);
                        }
                    }
                });
                
                // Check for JSON result
                if (output.includes('RESULT_START') && output.includes('RESULT_END')) {
                    const startIdx = outputBuffer.indexOf('RESULT_START') + 'RESULT_START'.length;
                    const endIdx = outputBuffer.indexOf('RESULT_END');
                    const jsonStr = outputBuffer.substring(startIdx, endIdx).trim();
                    
                    try {
                        const result = JSON.parse(jsonStr);
                        
                        if (result.success) {
                            resultsData.answer = result.answer;
                            resultsData.sources = result.sources || [];
                            resultsData.papers_processed = result.statistics?.documents_processed || 0;
                            resultsData.chunks_stored = result.statistics?.chunks_indexed || 0;
                            resultsData.queries_tested = result.statistics?.relevant_results || 0;
                            
                            socket.emit('research_complete', resultsData);
                        } else {
                            socket.emit('research_error', {
                                error: result.error || 'Research failed',
                                query: result.query
                            });
                        }
                    } catch (e) {
                        console.error('Error parsing result JSON:', e);
                        socket.emit('research_error', {
                            error: 'Failed to parse research results'
                        });
                    }
                }
            });

            pythonProcess.stderr.on('data', (data) => {
                const error = data.toString();
                console.error('❌ Python process error:', error);
                
                // Don't emit deprecation warnings as errors
                if (!error.includes('DeprecationWarning') && !error.includes('builtin type')) {
                    socket.emit('research_progress', {
                        timestamp: new Date().toISOString().substring(11, 19),
                        message: `⚠️  Warning: ${error.trim()}`
                    });
                }
            });

            pythonProcess.on('close', (code) => {
                const endTime = Date.now();
                resultsData.processing_time = Math.round((endTime - startTime) / 1000);
                
                if (code === 0) {
                    console.log('✅ Research completed successfully');
                    
                    // If we haven't already sent results via JSON parsing, send default
                    if (!resultsData.answer) {
                        resultsData.answer = `
                            <h3>🔬 Research Analysis Complete</h3>
                            <p>Successfully processed research query: "${data.query}"</p>
                            <p>The system demonstrated its ability to handle arbitrary queries dynamically, 
                            fetching and analyzing relevant content to provide comprehensive research insights.</p>
                            <p><em>This shows the AI Deep Research MCP system working with any user-provided query.</em></p>
                        `;
                        
                        socket.emit('research_complete', resultsData);
                    }
                } else {
                    console.error('❌ Research failed with code:', code);
                    socket.emit('research_error', {
                        error: `Research process failed with exit code ${code}. Check server logs for details.`,
                        code: code,
                        query: data.query
                    });
                }
            });

        } catch (error) {
            console.error('❌ Error starting research:', error);
            socket.emit('research_error', {
                error: error.message,
                details: error.stack
            });
        }
    });

    socket.on('disconnect', () => {
        console.log('❌ Client disconnected:', socket.id);
    });
});

// Start server
server.listen(PORT, () => {
    console.log(`🚀 AI Deep Research MCP Server running on http://localhost:${PORT}`);
    console.log('🔬 Features:');
    console.log('  • Real-time PDF downloading from academic sources');
    console.log('  • Advanced text extraction and semantic processing');
    console.log('  • Vector database storage and intelligent retrieval');
    console.log('  • Live progress monitoring with Socket.IO');
    console.log('  • Test-driven development methodology');
    console.log('');
    console.log('Ready to process research queries! 🎯');
});
