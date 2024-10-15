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
      id: this.todos.length + 1,
      task: task,
      completed: false
    };
    this.todos.push(newTodo);
    this.saveTodos();
    return newTodo;
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

  listTodos(): Todo[] {
    return this.todos;
  }
}

export const func = ({ command }: { command: string }): string => {
  const todoManager = new TodoListManager();

  // Parse the command to extract action, task, and id
  const { action, task, id } = parseCommand(command);

  switch (action) {
    case 'add':
      if (task) {
        const newTodo = todoManager.addTodo(task);
        return JSON.stringify({ success: true, message: 'Todo added successfully', todo: newTodo });
      }
      return JSON.stringify({ success: false, error: 'Task is required for adding a todo' });

    case 'update':
      if (id !== undefined && task) {
        const updatedTodo = todoManager.updateTodoList(id, task);
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

    default:
      return JSON.stringify({ success: false, error: 'Invalid action' });
  }
};

function parseCommand(command: string): { action: string; task?: string; id?: number } {
  const words = command.toLowerCase().split(' ');
  let action = '';
  let task = '';
  let id: number | undefined;

  if (words.includes('add') || words.includes('create')) {
    action = 'add';
    task = words.slice(words.indexOf('add') + 1).join(' ');
  } else if (words.includes('update') || words.includes('edit')) {
    action = 'update';
    id = parseInt(words[words.indexOf('update') + 1]);
    task = words.slice(words.indexOf('to') + 1).join(' ');
  } else if (words.includes('toggle') || words.includes('complete')) {
    action = 'toggle';
    id = parseInt(words[words.indexOf('toggle') + 1]);
  } else if (words.includes('delete') || words.includes('remove')) {
    action = 'delete';
    id = parseInt(words[words.indexOf('delete') + 1]);
  } else if (words.includes('list') || words.includes('show')) {
    action = 'list';
  }

  return { action, task, id };
}

export const object = {
  name: 'todo_manager',
  description: 'Manage a to-do list with natural language commands to add, update, toggle completion, delete, and list todos.',
  parameters: {
    type: 'object',
    properties: {
      command: {
        type: 'string',
        description: 'A natural language command to perform an action on the todo list'
      }
    },
    required: ['command']
  }
};
