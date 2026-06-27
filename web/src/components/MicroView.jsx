import { useState, useRef } from 'react';

/**
 * MicroView — Daily habits checklist with edit mode.
 */
export default function MicroView({ data, setData, microConfig, setMicroConfig }) {
  const [editMode, setEditMode] = useState(false);
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const toggleStatus = (id) => {
    setData(prev => ({
      ...prev,
      microStatus: {
        ...prev.microStatus,
        [id]: !prev.microStatus[id],
      },
    }));
  };

  const addHabit = () => {
    const text = input.trim();
    if (!text) return;
    const newId = microConfig.length > 0 ? Math.max(...microConfig.map(t => t.id)) + 1 : 1;
    setMicroConfig(prev => [...prev, { id: newId, text }]);
    setInput('');
    inputRef.current?.focus();
  };

  const deleteHabit = (id) => {
    setMicroConfig(prev => prev.filter(t => t.id !== id));
    setData(prev => {
      const status = { ...prev.microStatus };
      delete status[id];
      return { ...prev, microStatus: status };
    });
  };

  const renameHabit = (id, newText) => {
    if (!newText.trim()) return;
    setMicroConfig(prev => prev.map(t =>
      t.id === id ? { ...t, text: newText.trim() } : t
    ));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') addHabit();
  };

  return (
    <div className="micro-view glass">
      <div className="micro-view__header">
        <span className="micro-view__title">⚡  Daily Habits</span>
        <button
          className={`btn-pill btn-pill--sm ${editMode ? 'btn-pill--accent' : 'btn-pill--ghost'}`}
          onClick={() => setEditMode(!editMode)}
        >
          {editMode ? '✓ Done' : '✏ Edit'}
        </button>
      </div>

      <div className="micro-view__list">
        {microConfig.length === 0 ? (
          <div className="task-panel__empty">No habits added yet!</div>
        ) : (
          microConfig.map(task => {
            const isDone = !!data.microStatus[task.id];
            return (
              <div key={task.id} className="task-card">
                {editMode ? (
                  <EditableCard
                    task={task}
                    onRename={renameHabit}
                    onDelete={deleteHabit}
                  />
                ) : (
                  <>
                    <input
                      type="checkbox"
                      className="task-card__checkbox micro-card__checkbox"
                      checked={isDone}
                      onChange={() => toggleStatus(task.id)}
                    />
                    <span className={`task-card__text ${isDone ? 'task-card__text--done' : ''}`}>
                      {task.text}
                    </span>
                    {isDone && <span className="micro-card__done-mark">✓</span>}
                  </>
                )}
              </div>
            );
          })
        )}
      </div>

      <div className="micro-view__input-row">
        <input
          ref={inputRef}
          className="task-panel__input"
          placeholder="Add a new habit..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="btn-pill btn-pill--accent btn-pill--sm" onClick={addHabit}>
          + Add Habit
        </button>
      </div>
    </div>
  );
}

function EditableCard({ task, onRename, onDelete }) {
  const [text, setText] = useState(task.text);

  return (
    <>
      <input
        className="task-panel__input"
        value={text}
        onChange={e => setText(e.target.value)}
        style={{ marginRight: 8 }}
      />
      <button
        className="btn-pill btn-pill--success btn-pill--sm"
        onClick={() => onRename(task.id, text)}
        style={{ padding: '0 12px', minWidth: 'auto' }}
      >
        ✓
      </button>
      <button
        className="btn-pill btn-pill--sm"
        onClick={() => onDelete(task.id)}
        style={{ padding: '0 12px', minWidth: 'auto', background: 'var(--danger)', color: '#fff', marginLeft: 4 }}
      >
        ✕
      </button>
    </>
  );
}
