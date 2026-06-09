import { useState } from 'react';
import { Sidebar, type ViewType } from './components/Sidebar';
import { PlaygroundView } from './views/PlaygroundView';
import { DatasetExplorerView } from './views/DatasetExplorerView';
import { KnowledgeBaseView } from './views/KnowledgeBaseView';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('playground');

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden selection:bg-primary/30 selection:text-white">
      <Sidebar currentView={currentView} onChangeView={setCurrentView} />
      
      <main className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="h-full w-full absolute inset-0"
          >
            {currentView === 'playground' && <PlaygroundView />}
            {currentView === 'dataset' && <DatasetExplorerView />}
            {currentView === 'knowledge' && <KnowledgeBaseView />}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
