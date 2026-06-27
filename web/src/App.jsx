import { useState, useCallback, useEffect } from 'react';
import { useDailyData, useMicroConfig } from './hooks/useLocalStorage';
import { useTimer } from './hooks/useTimer';
import { useTheme } from './hooks/useTheme';
import { useEnforcer } from './hooks/useEnforcer';
import { playOnce } from './utils/audioManager';
import { generatePDF } from './utils/pdfGenerator';
import { getLocalTimeKey } from './utils/localDate';

import Navbar from './components/Navbar';
import ProgressDashboard from './components/ProgressDashboard';
import PomodoroTimer from './components/PomodoroTimer';
import MacroView from './components/MacroView';
import MicroView from './components/MicroView';
import BreakPrompt from './components/BreakPrompt';
import EnforcerModal from './components/EnforcerModal';
import SettingsPanel from './components/SettingsPanel';

export default function App() {
  const [data, setData] = useDailyData();
  const [microConfig, setMicroConfig] = useMicroConfig();
  const { bgUrl, allBackgrounds, setBackground, addCustomBackground, panelTransparency, setPanelTransparency } = useTheme();
  const { showEnforcer, resetTimer: resetEnforcer } = useEnforcer();

  const [mode, setMode] = useState('macro');
  const [showBreakPrompt, setShowBreakPrompt] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showPomodoroSettings, setShowPomodoroSettings] = useState(false);
  const [musicPauseSignal, setMusicPauseSignal] = useState(0);

  // Pomodoro timer
  const timer = useTimer(data.pomodoroWorkMin, data.pomodoroBreakMin);
  const { onComplete, startBreak, startWork } = timer;

  // Timer completion handler
  useEffect(() => {
    onComplete((wasBreak) => {
      setMusicPauseSignal(signal => signal + 1);
      playOnce();
      if (wasBreak) {
        // Break ended
        setShowBreakPrompt(true);
      } else {
        // Work session ended — increment sessions
        setData(prev => ({
          ...prev,
          pomodoroSessions: prev.pomodoroSessions + 1,
        }));
        setShowBreakPrompt(true);
      }
    });
  }, [onComplete, setData]);

  // Break prompt actions
  const handleBreak = useCallback(() => {
    setShowBreakPrompt(false);
    startBreak();
  }, [startBreak]);

  const handleMicro = useCallback(() => {
    setShowBreakPrompt(false);
    setMode('micro');
  }, []);

  const handleContinue = useCallback(() => {
    setShowBreakPrompt(false);
    startWork();
  }, [startWork]);

  // Enforcer submit
  const handleEnforcerSubmit = useCallback((text) => {
    setData(prev => ({
      ...prev,
      enforcerLogs: [
        ...prev.enforcerLogs,
        { timestamp: getLocalTimeKey(), text },
      ],
    }));
    resetEnforcer();
  }, [setData, resetEnforcer]);

  // PDF download
  const handlePdf = useCallback(() => {
    generatePDF(data, microConfig);
  }, [data, microConfig]);

  return (
    <>
      {/* Background Layer */}
      <div
        className="app-background"
        style={{ backgroundImage: `url(${bgUrl})` }}
      />

      {/* Main UI */}
      <div className="app-container">
        <Navbar
          onSettings={() => setShowSettings(true)}
          onPdf={handlePdf}
        />

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-toggle__btn ${mode === 'macro' ? 'mode-toggle__btn--active' : ''}`}
            onClick={() => setMode('macro')}
          >
            📚  Macro Tasks
          </button>
          <button
            className={`mode-toggle__btn ${mode === 'micro' ? 'mode-toggle__btn--active' : ''}`}
            onClick={() => setMode('micro')}
          >
            ⚡  Micro Tasks
          </button>
        </div>

        {/* Progress Dashboard */}
        <ProgressDashboard
          data={data}
          microConfig={microConfig}
          musicPauseSignal={musicPauseSignal}
        />

        {/* Content Area */}
        <div className="content-area">
          {mode === 'macro' ? (
            <>
              <MacroView data={data} setData={setData} />
              <PomodoroTimer
                timer={timer}
                sessions={data.pomodoroSessions}
                onSettingsClick={() => setShowPomodoroSettings(true)}
              />
            </>
          ) : (
            <MicroView
              data={data}
              setData={setData}
              microConfig={microConfig}
              setMicroConfig={setMicroConfig}
            />
          )}
        </div>
      </div>

      {/* Modals */}
      {showBreakPrompt && (
        <BreakPrompt
          onBreak={handleBreak}
          onMicro={handleMicro}
          onContinue={handleContinue}
        />
      )}

      {showEnforcer && (
        <EnforcerModal onSubmit={handleEnforcerSubmit} />
      )}

      {showSettings && (
        <SettingsPanel
          bgUrl={bgUrl}
          allBackgrounds={allBackgrounds}
          setBackground={setBackground}
          addCustomBackground={addCustomBackground}
          panelTransparency={panelTransparency}
          setPanelTransparency={setPanelTransparency}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Pomodoro Settings Dialog */}
      {showPomodoroSettings && (
        <PomodoroSettingsDialog
          data={data}
          setData={setData}
          onClose={() => setShowPomodoroSettings(false)}
        />
      )}
    </>
  );
}

function PomodoroSettingsDialog({ data, setData, onClose }) {
  const [workMin, setWorkMin] = useState(data.pomodoroWorkMin);
  const [breakMin, setBreakMin] = useState(data.pomodoroBreakMin);

  const save = () => {
    const w = parseInt(workMin) || 25;
    const b = parseInt(breakMin) || 10;
    setData(prev => ({
      ...prev,
      pomodoroWorkMin: Math.max(1, w),
      pomodoroBreakMin: Math.max(1, b),
    }));
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card glass-surface" style={{ maxWidth: 380 }} onClick={e => e.stopPropagation()}>
        <div className="modal-card__title" style={{ fontSize: 18 }}>⚙  Timer Settings</div>
        <div className="modal-card__subtitle">Customize your Pomodoro durations</div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span style={{ fontSize: 14 }}>Work duration (min):</span>
          <input
            className="task-panel__input"
            type="number"
            min={1}
            value={workMin}
            onChange={e => setWorkMin(e.target.value)}
            style={{ width: 80, textAlign: 'center' }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <span style={{ fontSize: 14 }}>Break duration (min):</span>
          <input
            className="task-panel__input"
            type="number"
            min={1}
            value={breakMin}
            onChange={e => setBreakMin(e.target.value)}
            style={{ width: 80, textAlign: 'center' }}
          />
        </div>

        <button className="btn-pill btn-pill--accent" onClick={save} style={{ width: '100%' }}>
          Save
        </button>
      </div>
    </div>
  );
}
