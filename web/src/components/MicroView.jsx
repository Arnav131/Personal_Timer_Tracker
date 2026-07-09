import { useState, useRef } from 'react';
import PixelIcon from './PixelIcon';

/**
 * MicroView - Daily habits checklist with edit mode.
 */
export default function MicroView({ data, setData, microConfig, setMicroConfig }) {
  const [editMode, setEditMode] = useState(false);
  const [input, setInput] = useState('');
  const inputRef = useRef(null);
  const hasHabits = microConfig.length > 0;

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
    window.requestAnimationFrame(() => inputRef.current?.focus());
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

  const addInput = (
    <input
      ref={inputRef}
      className="task-panel__input"
      placeholder="Add a new habit..."
      value={input}
      onChange={e => setInput(e.target.value)}
      onKeyDown={handleKeyDown}
    />
  );

  return (
    <div className="micro-view glass">
      <div className="micro-view__header">
        <span className="micro-view__title">
          <PixelIcon name="bolt" size="sm" />
          Daily Habits
        </span>
        <button
          className={`btn-pill btn-pill--sm ${editMode ? 'btn-pill--accent' : 'btn-pill--ghost'}`}
          onClick={() => setEditMode(!editMode)}
        >
          <PixelIcon name={editMode ? 'check' : 'edit'} size="xs" />
          {editMode ? 'Done' : 'Edit'}
        </button>
      </div>

      <div className={`micro-view__list ${hasHabits ? '' : 'micro-view__list--empty'}`}>
        {!hasHabits ? (
          <div className="micro-view__starter">
            <PixelIcon name="bolt" size="xl" />
            <div className="micro-view__starter-title">No habits yet</div>
            <div className="micro-view__starter-form">
              {addInput}
              <button className="btn-pill btn-pill--accent micro-view__starter-add" onClick={addHabit}>
                <PixelIcon name="check" size="xs" />
                Add First Habit
              </button>
            </div>
          </div>
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
                    {isDone && (
                      <span className="micro-card__done-mark">
                        <PixelIcon name="check" size="xs" />
                      </span>
                    )}
                  </>
                )}
              </div>
            );
          })
        )}
      </div>

      {hasHabits && (
        <div className="micro-view__input-row">
          {addInput}
          <button className="btn-pill btn-pill--accent btn-pill--sm" onClick={addHabit}>
            <PixelIcon name="check" size="xs" />
            Add Habit
          </button>
        </div>
      )}
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
        className="btn-pill btn-pill--success btn-pill--sm micro-edit-btn"
        onClick={() => onRename(task.id, text)}
        aria-label="Save habit"
      >
        <PixelIcon name="check" size="xs" />
      </button>
      <button
        className="btn-pill btn-pill--danger btn-pill--sm micro-edit-btn"
        onClick={() => onDelete(task.id)}
        aria-label="Delete habit"
      >
        <PixelIcon name="close" size="xs" />
      </button>
    </>
  );
}
