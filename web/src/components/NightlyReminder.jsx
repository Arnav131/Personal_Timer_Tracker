export default function NightlyReminder({ onDownload, onIgnore }) {
  const download = () => {
    onDownload();
    onIgnore();
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="nightly-reminder-title">
      <div className="modal-card glass-surface">
        <div className="modal-card__title" id="nightly-reminder-title">Save today’s report?</div>
        <div className="modal-card__subtitle">
          It is 11:45 PM. Today’s tasks reset at midnight, so download the PDF now if you want a copy.
        </div>
        <div className="modal-card__buttons">
          <button className="btn-pill btn-pill--accent" onClick={download}>Download PDF</button>
          <button className="btn-pill btn-pill--ghost" onClick={onIgnore}>Ignore tonight</button>
        </div>
      </div>
    </div>
  );
}
