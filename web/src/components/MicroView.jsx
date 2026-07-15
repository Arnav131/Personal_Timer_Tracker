import { useState, useRef } from 'react';
import PixelIcon from './PixelIcon';

const MICRO_TASK_DESCRIPTION = 'Micro tasks are small, self-contained actions that can be completed quickly with minimal cognitive effort and without materially interrupting primary productivity goals.';

/**
 * MicroView - Daily micro task list.
 */
export default function MicroView({ data, setData }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);
  const microTasks = data.microTasks || [];
  const hasTasks = microTasks.length > 0;

  const addTask = () => {
    const text = input.trim();
    if (!text) return;
    const newId = microTasks.length > 0 ? Math.max(...microTasks.map(t => t.id)) + 1 : 1;
    setData(prev => ({
      ...prev,
      microTasks: [...(prev.microTasks || []), { id: newId, text, done: false }],
    }));
    setInput('');
    window.requestAnimationFrame(() => inputRef.current?.focus());
  };

  const toggleTask = (id) => {
    setData(prev => ({
      ...prev,
      microTasks: (prev.microTasks || []).map(t =>
        t.id === id ? { ...t, done: !t.done } : t
      ),
    }));
  };

  const deleteTask = (id) => {
    setData(prev => ({
      ...prev,
      microTasks: (prev.microTasks || []).filter(t => t.id !== id),
    }));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') addTask();
  };

  const addInput = (
    <input
      ref={inputRef}
      className="task-panel__input"
      placeholder="Add a micro task..."
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
          Micro Tasks
        </span>
      </div>

      {!hasTasks ? (
        <div className="micro-view__starter-shell">
          <div className="micro-view__starter">
            <PixelIcon name="bolt" size="xl" />
            <div className="micro-view__starter-title">Start with one micro task</div>
            <p className="micro-view__starter-description">{MICRO_TASK_DESCRIPTION}</p>
            <div className="micro-view__starter-form">
              {addInput}
              <button className="btn-pill btn-pill--accent micro-view__starter-add" onClick={addTask}>
                <PixelIcon name="check" size="xs" />
                Add Micro Task
              </button>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="micro-view__input-row">
            {addInput}
            <button className="btn-pill btn-pill--accent btn-pill--sm" onClick={addTask}>
              <PixelIcon name="check" size="xs" />
              Add Task
            </button>
          </div>

          <div className="micro-view__list">
            {microTasks.map(task => (
              <div key={task.id} className="task-card">
                <input
                  type="checkbox"
                  className="task-card__checkbox micro-card__checkbox"
                  checked={task.done}
                  onChange={() => toggleTask(task.id)}
                />
                <span className={`task-card__text ${task.done ? 'task-card__text--done' : ''}`}>
                  {task.text}
                </span>
                <button className="task-card__delete" onClick={() => deleteTask(task.id)} aria-label="Delete micro task">
                  <PixelIcon name="close" size="xs" />
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
