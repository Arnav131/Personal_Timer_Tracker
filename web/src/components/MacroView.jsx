import { useState, useRef } from 'react';

/**
 * MacroView — Task list panel (left side of macro view).
 */
export default function MacroView({ data, setData }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const addTask = () => {
    const text = input.trim();
    if (!text) return;
    const tasks = data.macroTasks;
    const newId = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;
    setData(prev => ({
      ...prev,
      macroTasks: [...prev.macroTasks, { id: newId, text, done: false }],
    }));
    setInput('');
    inputRef.current?.focus();
  };

  const toggleTask = (id) => {
    setData(prev => ({
      ...prev,
      macroTasks: prev.macroTasks.map(t =>
        t.id === id ? { ...t, done: !t.done } : t
      ),
    }));
  };

  const deleteTask = (id) => {
    setData(prev => ({
      ...prev,
      macroTasks: prev.macroTasks.filter(t => t.id !== id),
    }));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') addTask();
  };

  return (
    <div className="task-panel glass">
      <div className="task-panel__header">📝  To-Do List</div>

      <div className="task-panel__input-row">
        <input
          ref={inputRef}
          className="task-panel__input"
          placeholder="Add a new task..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="task-panel__add-btn" onClick={addTask}>+</button>
      </div>

      <div className="task-panel__list">
        {data.macroTasks.length === 0 ? (
          <div className="task-panel__empty">No tasks yet. Add one above!</div>
        ) : (
          data.macroTasks.map(task => (
            <div key={task.id} className="task-card">
              <input
                type="checkbox"
                className="task-card__checkbox"
                checked={task.done}
                onChange={() => toggleTask(task.id)}
              />
              <span className={`task-card__text ${task.done ? 'task-card__text--done' : ''}`}>
                {task.text}
              </span>
              <button className="task-card__delete" onClick={() => deleteTask(task.id)}>✕</button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
