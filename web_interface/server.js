const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main HTML page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API endpoint for research queries
app.post('/api/research', async (req, res) => {
  try {
    const { query, maxSources = 5, maxDepth = 2, citationStyle = 'APA' } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // Emit progress to connected clients
    io.emit('research-started', { query, maxSources, maxDepth });

    // Execute the Python research system
    const pythonProcess = spawn('python', [
      '-c', 
      `
import sys
import os
import asyncio
import logging

# Suppress all logging to prevent interference with JSON output
logging.basicConfig(level=logging.CRITICAL)
for logger_name in ['src.embedder', 'src.vector_store', 'src.api_orchestrator', 
                    'sentence_transformers.SentenceTransformer', 'src.citation_manager']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

sys.path.insert(0, '/Users/jessicadoner/0. Knowledge Manager/ai_deep_research_mcp')

async def run_research():
    try:
        from src.api_orchestrator import APIOrchestrator, ResearchRequest
        
        orchestrator = APIOrchestrator()
        
        request = ResearchRequest(
            query="${query.replace(/"/g, '\\"')}",
            max_sources=${maxSources},
            max_depth=${maxDepth},
            citation_style="${citationStyle}"
        )
        
        # Progress callback to emit updates
        async def progress_callback(progress):
            print(f"PROGRESS: {progress.stage} - {progress.message}")
        
        print("Starting research...")
        response = await orchestrator.conduct_research(request, progress_callback=progress_callback)
        
        # Output the result as JSON
        import json
        result = {
            "success": response.success,
            "query": response.query,
            "answer": response.answer,
            "sources": response.sources,
            "bibliography": response.bibliography,
            "execution_time": response.execution_time,
            "metadata": response.metadata
        }
        print("RESULT:" + json.dumps(result))
        
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {traceback.format_exc()}")

asyncio.run(run_research())
      `
    ], {
      cwd: '/Users/jessicadoner/0. Knowledge Manager/ai_deep_research_mcp'
    });

    let output = '';
    let errorOutput = '';
    let result = null;

    pythonProcess.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      
      // Check for progress updates
      if (text.includes('PROGRESS:')) {
        const progressLine = text.split('PROGRESS:')[1].trim();
        io.emit('research-progress', { message: progressLine });
      }
      
      // Check for final result
      if (text.includes('RESULT:')) {
        try {
          // Extract just the JSON part, stopping at newline
          const resultPart = text.split('RESULT:')[1];
          const jsonStr = resultPart.split('\n')[0].trim();
          result = JSON.parse(jsonStr);
        } catch (e) {
          console.error('Failed to parse result JSON:', e);
          console.error('Raw text:', text);
          console.error('Extracted JSON string:', resultPart ? resultPart.split('\n')[0] : 'N/A');
        }
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Python stderr:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code === 0 && result) {
        io.emit('research-completed', result);
        res.json(result);
      } else {
        const error = `Research process failed with code ${code}. Error: ${errorOutput}`;
        io.emit('research-error', { error });
        res.status(500).json({ error, output, errorOutput });
      }
    });

  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`🚀 AI Deep Research Web Interface running on http://localhost:${PORT}`);
  console.log(`📊 Real-time updates via Socket.IO`);
  console.log(`🔬 Ready to conduct deep research queries!`);
});
