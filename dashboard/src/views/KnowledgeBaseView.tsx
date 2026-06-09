import { Database, Network, KeyRound, BookOpen, Search, ArrowRight } from 'lucide-react';

export function KnowledgeBaseView() {
  const dictionaryPairs = [
    { en: "relax", ta: ["relax aaguradhu", "chill panradhu", "cool ah iru"] },
    { en: "friend", ta: ["macha", "machi", "nanba", "bro", "maplei"] },
    { en: "angry", ta: ["semma gaandu", "kovam", "kaduppu", "tension"] },
    { en: "money", ta: ["kaasu", "thuttu", "panam", "dhuddu"] },
    { en: "eat", ta: ["vettu vettu nu vetturadhu", "full kattu", "saapadu"] },
    { en: "sleep", ta: ["thookkam", "korattai", "kuttai pottu thoongu"] },
    { en: "scared", ta: ["bayam", "jerk aaguradhu", "nadu nadungi"] },
    { en: "fast", ta: ["jet speed", "parandhu", "vegam", "sirutha"] },
  ];

  return (
    <div className="flex flex-col h-full p-6 max-w-7xl mx-auto w-full gap-8">
      {/* Top Section: DB Stats */}
      <div>
        <h2 className="text-3xl font-bold text-text mb-2">Knowledge Base Monitor</h2>
        <p className="text-text-muted mb-6">Monitor the Qdrant vector database and inspect the local slang dictionary.</p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface border border-border p-5 rounded-xl shadow-sm hover:border-primary/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-primary/10 rounded-lg text-primary"><Database size={20} /></div>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">CONNECTED</span>
            </div>
            <p className="text-sm text-text-muted mb-1">Collection Name</p>
            <p className="text-lg font-bold text-text">dailydialog_slang_kb</p>
          </div>

          <div className="bg-surface border border-border p-5 rounded-xl shadow-sm hover:border-primary/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Network size={20} /></div>
            </div>
            <p className="text-sm text-text-muted mb-1">Vector Size</p>
            <p className="text-lg font-bold text-text">1024 <span className="text-xs font-normal text-text-muted">Dimensions</span></p>
            <p className="text-xs text-blue-400 mt-1">via BGE-M3 model</p>
          </div>

          <div className="bg-surface border border-border p-5 rounded-xl shadow-sm hover:border-primary/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-500/10 rounded-lg text-purple-400"><KeyRound size={20} /></div>
            </div>
            <p className="text-sm text-text-muted mb-1">Distance Metric</p>
            <p className="text-lg font-bold text-text">Cosine</p>
          </div>

          <div className="bg-surface border border-border p-5 rounded-xl shadow-sm hover:border-primary/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400"><BookOpen size={20} /></div>
            </div>
            <p className="text-sm text-text-muted mb-1">Total Payload Pairs</p>
            <p className="text-lg font-bold text-text">8,432</p>
            <p className="text-xs text-amber-400 mt-1">Indexed Entities</p>
          </div>
        </div>
      </div>

      {/* Dictionary Preview */}
      <div className="flex-1 flex flex-col min-h-0 bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-border flex justify-between items-center bg-background/30">
          <h3 className="font-semibold text-lg text-text flex items-center gap-2">
            <BookOpen size={18} className="text-primary" />
            Dictionary Payload Preview
          </h3>
          <div className="relative w-64">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input 
              type="text" 
              placeholder="Search dictionary..." 
              className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-1.5 text-sm text-text placeholder-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-auto p-5">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {dictionaryPairs.map((pair, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-background border border-border rounded-xl group hover:border-primary/30 transition-colors">
                <div className="flex items-center gap-4 w-2/5">
                  <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1">English Keyword</div>
                  <div className="text-base font-medium text-text bg-surface px-3 py-1.5 rounded-lg border border-border group-hover:border-primary/50 transition-colors">
                    {pair.en}
                  </div>
                </div>
                
                <ArrowRight size={18} className="text-text-muted opacity-50" />
                
                <div className="w-[55%]">
                  <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Retrieved Phrasing</div>
                  <div className="flex flex-wrap gap-2">
                    {pair.ta.map((slang, i) => (
                      <span key={i} className="text-sm px-2.5 py-1 bg-primary/10 text-primary border border-primary/20 rounded-md">
                        {slang}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
