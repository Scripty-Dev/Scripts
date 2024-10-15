import * as fs from 'fs';

interface Todo {
  id: number;
  task: string;
  completed: boolean;
}

class TodoListManager {
  private todos: Todo[] = [];
  private filename: string;

  constructor(filename: string = 'todos.json') {
    this.filename = filename;
    this.loadTodos();
  }

  private loadTodos(): void {
    try {
      const data = fs.readFileSync(this.filename, 'utf-8');
      this.todos = JSON.parse(data);
    } catch (error) {
      this.todos = [];
    }
  }

  private saveTodos(): void {
    const data = JSON.stringify(this.todos, null, 2);
    fs.writeFileSync(this.filename, data, 'utf-8');
  }

  addTodo(task: string): Todo {
    const newTodo: Todo = {
      id: this.todos.length > 0 ? Math.max(...this.todos.map(t => t.id)) + 1 : 1,
      task: task,
      completed: false
    };
    this.todos.push(newTodo);
    this.saveTodos();
    return newTodo;
  }

  addMultipleTodos(tasks: string[]): Todo[] {
    const newTodos = tasks.map(task => this.addTodo(task));
    return newTodos;
  }

  updateTodoList(id: number, updatedTask: string): Todo | null {
    const todoIndex = this.todos.findIndex(todo => todo.id === id);
    if (todoIndex !== -1) {
      this.todos[todoIndex].task = updatedTask;
      this.saveTodos();
      return this.todos[todoIndex];
    }
    return null;
  }

  toggleTodoCompletion(id: number): Todo | null {
    const todoIndex = this.todos.findIndex(todo => todo.id === id);
    if (todoIndex !== -1) {
      this.todos[todoIndex].completed = !this.todos[todoIndex].completed;
      this.saveTodos();
      return this.todos[todoIndex];
    }
    return null;
  }

  deleteTodo(id: number): boolean {
    const todoIndex = this.todos.findIndex(todo => todo.id === id);
    if (todoIndex !== -1) {
      this.todos.splice(todoIndex, 1);
      this.saveTodos();
      return true;
    }
    return false;
  }

  clearAllTodos(): void {
    this.todos = [];
    this.saveTodos();
  }

  listTodos(): Todo[] {
    return this.todos;
  }
}

export const func = ({ action, tasks, id }: { action: string; tasks?: string | string[]; id?: number }): string => {
  const todoManager = new TodoListManager();

  switch (action) {
    case 'add':
      if (Array.isArray(tasks)) {
        const newTodos = todoManager.addMultipleTodos(tasks);
        return JSON.stringify({ success: true, message: 'Multiple todos added successfully', todos: newTodos });
      } else if (tasks) {
        const newTodo = todoManager.addTodo(tasks);
        return JSON.stringify({ success: true, message: 'Todo added successfully', todo: newTodo });
      }
      return JSON.stringify({ success: false, error: 'Task(s) are required for adding todo(s)' });

    case 'update':
      if (id !== undefined && typeof tasks === 'string') {
        const updatedTodo = todoManager.updateTodoList(id, tasks);
        return updatedTodo
          ? JSON.stringify({ success: true, message: 'Todo updated successfully', todo: updatedTodo })
          : JSON.stringify({ success: false, error: 'Todo not found' });
      }
      return JSON.stringify({ success: false, error: 'ID and task are required for updating a todo' });

    case 'toggle':
      if (id !== undefined) {
        const toggledTodo = todoManager.toggleTodoCompletion(id);
        return toggledTodo
          ? JSON.stringify({ success: true, message: 'Todo completion toggled successfully', todo: toggledTodo })
          : JSON.stringify({ success: false, error: 'Todo not found' });
      }
      return JSON.stringify({ success: false, error: 'ID is required for toggling a todo' });

    case 'delete':
      if (id !== undefined) {
        const deleted = todoManager.deleteTodo(id);
        return deleted
          ? JSON.stringify({ success: true, message: 'Todo deleted successfully' })
          : JSON.stringify({ success: false, error: 'Todo not found' });
      }
      return JSON.stringify({ success: false, error: 'ID is required for deleting a todo' });

    case 'list':
      const todos = todoManager.listTodos();
      return JSON.stringify({ success: true, todos: todos });

    case 'clear':
      todoManager.clearAllTodos();
      return JSON.stringify({ success: true, message: 'All todos cleared successfully' });

    default:
      return JSON.stringify({ success: false, error: 'Invalid action' });
  }
};

export const object = {
  name: 'todo_manager',
  description: 'Manage a to-do list with actions to add (single or multiple), update, toggle completion, delete, list, and clear all todos.',
  parameters: {
    type: 'object',
    properties: {
      action: {
        type: 'string',
        enum: ['add', 'update', 'toggle', 'delete', 'list', 'clear'],
        description: 'The action to perform on the todo list'
      },
      tasks: {
        oneOf: [
          { type: 'string' },
          { type: 'array', items: { type: 'string' } }
        ],
        description: 'The task(s) to add or update. For "add" action, this can be a single task (string) or multiple tasks (array of strings). For "update" action, this should be a single task (string).'
      },
      id: {
        type: 'number',
        description: 'The ID of the todo item (required for update, toggle, and delete actions)'
      }
    },
    required: ['action'],
    anyOf: [
      { required: ['action'], properties: { action: { enum: ['list', 'clear'] } } },
      { required: ['action', 'tasks'], properties: { action: { const: 'add' } } },
      { required: ['action', 'id', 'tasks'], properties: { action: { const: 'update' } } },
      { required: ['action', 'id'], properties: { action: { enum: ['toggle', 'delete'] } } }
    ]
  }
};
