import { PlaySquare, Database, LibraryBig, Settings, Activity } from 'lucide-react';
import { cn } from '../lib/utils';

export type ViewType = 'playground' | 'dataset' | 'knowledge';

interface SidebarProps {
  currentView: ViewType;
  onChangeView: (view: ViewType) => void;
}

export function Sidebar({ currentView, onChangeView }: SidebarProps) {
  const navItems = [
    { id: 'playground', label: 'Playground', icon: PlaySquare },
    { id: 'dataset', label: 'Dataset Explorer', icon: Database },
    { id: 'knowledge', label: 'Knowledge Base', icon: LibraryBig },
  ] as const;

  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col h-screen">
      <div className="p-6 flex items-center gap-3 border-b border-border">
        <div className="bg-primary/20 p-2 rounded-lg text-primary">
          <Activity size={24} />
        </div>
        <h1 className="font-bold text-xl text-text leading-tight tracking-tight">
          Colloquia<br/><span className="text-primary font-black"></span>
        </h1>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChangeView(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                isActive 
                  ? "bg-primary/10 text-primary border border-primary/20" 
                  : "text-text-muted hover:bg-white/5 hover:text-text"
              )}
            >
              <Icon size={18} className={cn(isActive && "fill-primary/20")} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-text-muted hover:bg-white/5 hover:text-text transition-all">
          <Settings size={18} />
          Settings
        </button>
      </div>
    </aside>
  );
}
