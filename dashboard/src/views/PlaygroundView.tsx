import { useState } from 'react';
import { Sparkles, Copy, Database, Wand2, SlidersHorizontal, ChevronRight, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function PlaygroundView() {
  const [inputText, setInputText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [outputs, setOutputs] = useState<any[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [contextExpanded, setContextExpanded] = useState(false);
  
  const examples = [
    "Say, Jim, how about going for a few beers after dinner?",
    "I'm feeling really exhausted today, need some rest.",
    "Did you watch the match last night? It was crazy!"
  ];

  const handleGenerate = async () => {
    if (!inputText.trim()) return;
    setIsGenerating(true);

    const sentencesArray = inputText
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    try {
      const response = await fetch("/api/translate-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ english_inputs: sentencesArray }),
      });

      const data = await response.json();
      setOutputs(data.results);
      setShowResults(true);
    } catch (error) {
      console.error("Translation generation failed:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!outputs || outputs.length === 0) return;
    
    let content = "=== Tanglish Conversions ===\n\n";
    outputs.forEach((item, index) => {
      content += `[Input ${index + 1}]: ${item.input_text}\n`;
      content += `[Variations]:\n`;
      item.candidates.forEach((cand: any) => {
        content += `  - Temp ${cand.temperature}: ${cand.tanglish}\n`;
      });
      content += "\n----------------------------------------\n\n";
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tanglish_results_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-full gap-6 p-6">
      {/* LEFT PANEL */}
      <div className="w-1/2 flex flex-col gap-6 h-full overflow-y-auto pr-2 pb-6">
        <div>
          <h2 className="text-2xl font-bold mb-2 text-text">Playground</h2>
          <p className="text-text-muted text-sm">Convert standard English to natural Tanglish.</p>
        </div>

        {/* Input Section */}
        <div className="flex flex-col gap-3">
          <label className="text-sm font-semibold text-text uppercase tracking-wider">English Input</label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full h-32 bg-surface/50 border border-border rounded-xl p-4 text-text placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all resize-none shadow-inner"
            placeholder="Type standard English dialogue here..."
          />
          <div className="flex flex-wrap gap-2 mt-1">
            {examples.map((ex, i) => (
              <button 
                key={i}
                onClick={() => setInputText(ex)}
                className="text-xs px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 text-text-muted hover:text-text transition-colors"
              >
                {ex.length > 30 ? ex.substring(0, 30) + "..." : ex}
              </button>
            ))}
          </div>
        </div>

        {/* Settings Card */}
        <div className="bg-surface border border-border rounded-xl p-5 mt-2">
          <div className="flex items-center gap-2 mb-4 text-text border-b border-border/50 pb-3">
            <SlidersHorizontal size={18} className="text-primary" />
            <h3 className="font-semibold">Generation Settings</h3>
          </div>
          
          <div className="space-y-5">
            <div className="flex justify-between items-center">
              <span className="text-sm text-text-muted">LLM Model</span>
              <span className="text-xs px-2.5 py-1 bg-primary/20 text-primary border border-primary/20 rounded-md font-mono">
                llama-3.3-70b-versatile
              </span>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-muted">Candidates</span>
                <span className="text-sm font-medium">3</span>
              </div>
              <input type="range" min="1" max="4" defaultValue="3" className="w-full accent-primary" />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-muted">Temperature Range</span>
              </div>
              <div className="flex gap-2">
                {[0.5, 0.8, 1.0, 1.2].map((temp, i) => (
                  <div key={i} className={`flex-1 text-center py-1.5 rounded text-xs border ${temp === 1.2 ? 'border-border text-text-muted' : 'border-primary/50 bg-primary/10 text-primary font-medium'}`}>
                    {temp}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button 
          onClick={handleGenerate}
          disabled={!inputText || isGenerating}
          className="mt-4 w-full py-4 rounded-xl bg-primary hover:bg-primary-hover text-white font-bold flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_30px_rgba(139,92,246,0.5)] disabled:opacity-50 disabled:shadow-none relative overflow-hidden group"
        >
          {isGenerating ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Wand2 size={20} className="group-hover:rotate-12 transition-transform" />
              Generate Variations
            </>
          )}
        </button>
      </div>

      {/* RIGHT PANEL */}
      <div className="w-1/2 h-full flex flex-col gap-4 overflow-y-auto pb-6 pl-2">
        <div className="flex justify-between items-center mb-2 px-1">
          <h2 className="text-lg font-semibold text-text">Outputs & Context</h2>
          {showResults && outputs.length > 0 && (
            <button 
              onClick={handleDownload}
              className="flex items-center gap-2 px-3 py-1.5 bg-surface border border-border hover:bg-white/5 rounded-lg text-sm text-text-muted hover:text-text transition-colors shadow-sm"
            >
              <Download size={14} />
              Export .txt
            </button>
          )}
        </div>
        
        {!showResults && !isGenerating ? (
          <div className="flex-1 flex flex-col items-center justify-center text-text-muted border border-dashed border-border rounded-xl bg-surface/30">
            <Sparkles size={48} className="opacity-20 mb-4" />
            <p>Enter text and generate to see results.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4 w-full">
            <AnimatePresence>
              {showResults && outputs.map((sentenceOutput, sIdx) => (
                <div key={sIdx} className="mb-6 last:mb-0">
                  <div className="text-sm text-text-muted mb-3 pb-2 border-b border-border/50">
                    Input: <span className="text-text">"{sentenceOutput.input_text}"</span>
                  </div>
                  <div className="flex flex-col gap-4">
                    {sentenceOutput.candidates.map((cand: any, i: number) => {
                      const mockScore = Math.floor(Math.random() * 20) + 75; // Generate a mock score for demo
                      return (
                        <motion.div 
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.15 }}
                          key={i} 
                          className="bg-surface border border-border rounded-xl p-5 shadow-sm hover:border-primary/50 transition-colors group relative overflow-hidden"
                        >
                          <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-primary/80 to-primary/20" />
                          
                          <div className="flex justify-between items-start mb-3">
                            <span className="text-xs px-2 py-1 bg-white/5 rounded text-text-muted border border-border">
                              Temp: {cand.temperature}
                            </span>
                            <button className="text-text-muted hover:text-text transition-colors p-1.5 rounded-md hover:bg-white/10">
                              <Copy size={16} />
                            </button>
                          </div>
                          
                          <p className="text-lg font-medium text-text mb-4">
                            "{cand.tanglish}"
                          </p>
                          
                          <div className="flex items-center gap-3 mt-4">
                            <span className="text-xs font-semibold text-text-muted uppercase">Naturalness</span>
                            <div className="flex-1 h-2 bg-background rounded-full overflow-hidden">
                              <div 
                                className={`h-full rounded-full ${mockScore > 90 ? 'bg-emerald-500' : mockScore > 80 ? 'bg-primary' : 'bg-amber-500'}`} 
                                style={{ width: `${mockScore}%` }} 
                              />
                            </div>
                            <span className="text-xs font-bold">{mockScore}/100</span>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </AnimatePresence>

            {showResults && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-4 border border-border rounded-xl overflow-hidden bg-background"
              >
                <button 
                  onClick={() => setContextExpanded(!contextExpanded)}
                  className="w-full p-4 flex justify-between items-center bg-surface hover:bg-surface/80 transition-colors"
                >
                  <div className="flex items-center gap-2 text-sm font-semibold text-text">
                    <Database size={16} className="text-primary" />
                    <span>🔍 Retrieved Slang RAG Context</span>
                  </div>
                  <ChevronRight size={18} className={`text-text-muted transition-transform duration-300 ${contextExpanded ? 'rotate-90' : ''}`} />
                </button>
                
                <AnimatePresence>
                  {contextExpanded && (
                    <motion.div 
                      initial={{ height: 0 }}
                      animate={{ height: "auto" }}
                      exit={{ height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 border-t border-border bg-[#0B0B0C] font-mono text-sm text-text-muted">
                        <div className="mb-2"><span className="text-primary">Matched keyword:</span> <span className="text-white">beers</span></div>
                        <div className="mb-4"><span className="text-primary">Slang terms:</span> <span className="text-white">beer adikka, sarakku, sillarai beers</span></div>
                        
                        <div className="mb-2"><span className="text-primary">Matched keyword:</span> <span className="text-white">Jim (friend)</span></div>
                        <div className="mb-2"><span className="text-primary">Slang terms:</span> <span className="text-white">macha, machi, bro</span></div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
