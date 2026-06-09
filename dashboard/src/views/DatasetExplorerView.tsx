import { Search, Download, CheckCircle2, Activity } from 'lucide-react';

export function DatasetExplorerView() {
  // Mock data for display
  const mockData = [
    { id: "DG-001", emotion: "happy", act: "inform", en: "Say, Jim, how about going for a few beers after dinner?", ta: "Macha Jim, dinner ku apram oru beer adikka polama?" },
    { id: "DG-002", emotion: "neutral", act: "question", en: "Do you know what time it is?", ta: "Time enna nu theriyuma?" },
    { id: "DG-003", emotion: "surprise", act: "directive", en: "Wow, that is incredibly expensive!", ta: "Adade, idhu romba expensive aache!" },
    { id: "DG-004", emotion: "sadness", act: "inform", en: "I don't feel like eating right now.", ta: "Enakku ippo sapida thonala." },
    { id: "DG-005", emotion: "anger", act: "commissive", en: "I will never talk to him again.", ta: "Na inime avan kitta pesa maaten." },
    { id: "DG-006", emotion: "happy", act: "inform", en: "We are going on a trip to the mountains.", ta: "Naanga mountains ku oru trip porom." },
    { id: "DG-007", emotion: "fear", act: "question", en: "Is someone standing outside the door?", ta: "Veliya yaro nikurangala?" },
    { id: "DG-008", emotion: "neutral", act: "inform", en: "I have finished my homework.", ta: "Na en homework ah mudichiten." },
  ];

  return (
    <div className="flex flex-col h-full p-6 max-w-7xl mx-auto w-full">
      {/* Top Hero Banner */}
      <div className="mb-8">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-3xl font-bold text-text mb-2">Dataset Explorer</h2>
            <p className="text-text-muted">Monitor and inspect the bulk generation pipeline.</p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors rounded-lg text-sm font-medium text-text">
            <Download size={16} />
            Export Full Dataset (.jsonl)
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-surface border border-border p-5 rounded-xl">
            <div className="text-sm text-text-muted mb-1 flex items-center gap-2">
              <DatabaseIcon className="w-4 h-4 text-primary" />
              Total Dataset Size
            </div>
            <div className="text-2xl font-bold text-text">13,118 <span className="text-sm font-normal text-text-muted">Utterances (DailyDialog)</span></div>
          </div>
          <div className="bg-surface border border-border p-5 rounded-xl">
            <div className="text-sm text-text-muted mb-1 flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              Target Output Style
            </div>
            <div className="text-2xl font-bold text-text">Latin-Script <span className="text-sm font-normal text-primary">Tanglish Only</span></div>
          </div>
          <div className="bg-surface border border-border p-5 rounded-xl flex items-center justify-between">
            <div>
              <div className="text-sm text-text-muted mb-1">System Status</div>
              <div className="text-lg font-bold text-emerald-400 flex items-center gap-2">
                <CheckCircle2 size={20} />
                Async Pipeline Ready
              </div>
            </div>
            <div className="w-12 h-12 rounded-full border-[3px] border-emerald-400/20 border-t-emerald-400 animate-spin" />
          </div>
        </div>
      </div>

      {/* Data Table Area */}
      <div className="flex-1 bg-surface border border-border rounded-xl flex flex-col overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border flex justify-between items-center bg-background/50">
          <div className="relative w-96">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input 
              type="text" 
              placeholder="Search by English text or emotion..." 
              className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text placeholder-text-muted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
            />
          </div>
          <div className="text-xs text-text-muted font-medium px-3 py-1 bg-white/5 rounded-md">
            Showing 8 of 13,118 entries
          </div>
        </div>
        
        <div className="overflow-auto flex-1">
          <table className="w-full text-left border-collapse min-w-max">
            <thead className="bg-background/80 sticky top-0 backdrop-blur-md z-10 border-b border-border">
              <tr>
                <th className="py-3 px-6 text-xs font-semibold text-text-muted uppercase tracking-wider">ID</th>
                <th className="py-3 px-6 text-xs font-semibold text-text-muted uppercase tracking-wider">Emotion</th>
                <th className="py-3 px-6 text-xs font-semibold text-text-muted uppercase tracking-wider">Dialogue Act</th>
                <th className="py-3 px-6 text-xs font-semibold text-text-muted uppercase tracking-wider">English Input</th>
                <th className="py-3 px-6 text-xs font-semibold text-text-muted uppercase tracking-wider">Best Tanglish Output</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockData.map((row, i) => (
                <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="py-4 px-6 text-sm text-text-muted font-mono">{row.id}</td>
                  <td className="py-4 px-6 text-sm">
                    <span className="px-2 py-1 bg-white/5 rounded border border-border/50 text-xs text-text-muted group-hover:border-primary/30 transition-colors">
                      {row.emotion}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-sm text-text-muted">{row.act}</td>
                  <td className="py-4 px-6 text-sm text-text max-w-xs truncate">{row.en}</td>
                  <td className="py-4 px-6 text-sm text-primary font-medium">{row.ta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DatabaseIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5V19A9 3 0 0 0 21 19V5" />
      <path d="M3 12A9 3 0 0 0 21 12" />
    </svg>
  );
}
