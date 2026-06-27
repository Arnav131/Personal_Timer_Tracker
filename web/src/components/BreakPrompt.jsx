/**
 * BreakPrompt — modal shown after Pomodoro session completion.
 */
export default function BreakPrompt({ onBreak, onMicro, onContinue }) {
  return (
    <div className="modal-overlay">
      <div className="modal-card glass-surface">
        <div className="modal-card__title">🎉  Session Complete!</div>
        <div className="modal-card__subtitle">Great work! What's next?</div>

        <div className="modal-card__buttons">
          <button className="btn-pill btn-pill--blue" onClick={onBreak}>
            ☕   Take a Break (10 min)
          </button>
          <button className="btn-pill btn-pill--soft" onClick={onMicro}>
            ⚡   Do a Micro Task
          </button>
          <button className="btn-pill btn-pill--success" onClick={onContinue}>
            📖   Continue Studying
          </button>
        </div>
      </div>
    </div>
  );
}
