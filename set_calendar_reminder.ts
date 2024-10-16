import { parseISO, addHours, addDays, addWeeks, startOfDay, format } from 'date-fns';
import { toZonedTime } from 'date-fns-tz';
import { BrowserWindow } from 'electron';

interface ReminderDetails {
  summary: string;
  description?: string;
  startDateTime: string;
  endDateTime?: string;
}

class GoogleCalendarManager {
  private static instance: GoogleCalendarManager;
  private timeZone: string;

  private constructor() {
    this.timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  }

  public static getInstance(): GoogleCalendarManager {
    if (!GoogleCalendarManager.instance) {
      GoogleCalendarManager.instance = new GoogleCalendarManager();
    }
    return GoogleCalendarManager.instance;
  }

  private parseDateTime(input: string): Date {
    const now = new Date();
    const lowercaseInput = input.toLowerCase();

    if (lowercaseInput === 'today') {
      return startOfDay(now);
    } else if (lowercaseInput === 'tomorrow') {
      return startOfDay(addDays(now, 1));
    } else if (lowercaseInput.startsWith('next')) {
      const parts = lowercaseInput.split(' ');
      if (parts[1] === 'week') {
        return startOfDay(addWeeks(now, 1));
      } else if (parts[1] === 'sunday' || parts[1] === 'monday' || parts[1] === 'tuesday' || parts[1] === 'wednesday' || parts[1] === 'thursday' || parts[1] === 'friday' || parts[1] === 'saturday') {
        const targetDay = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].indexOf(parts[1]);
        let daysToAdd = targetDay - now.getDay();
        if (daysToAdd <= 0) daysToAdd += 7;
        return startOfDay(addDays(now, daysToAdd));
      }
    }

    const parsedDate = parseISO(input);
    if (isNaN(parsedDate.getTime())) {
      throw new Error('Invalid date format');
    }
    return parsedDate;
  }

  public async createUserFriendlyReminder(reminderDetails: Partial<ReminderDetails>, token: string): Promise<any> {
    if (!reminderDetails.summary) {
      throw new Error('Summary is required');
    }

    if (!reminderDetails.startDateTime) {
      throw new Error('Start date/time is required');
    }

    const startDate = this.parseDateTime(reminderDetails.startDateTime);
    let endDate = reminderDetails.endDateTime ? this.parseDateTime(reminderDetails.endDateTime) : addHours(startDate, 1);

    const utcStartDate = toZonedTime(startDate, 'UTC');
    const utcEndDate = toZonedTime(endDate, 'UTC');

    const event = {
      summary: reminderDetails.summary,
      description: reminderDetails.description || '',
      start: {
        dateTime: format(utcStartDate, "yyyy-MM-dd'T'HH:mm:ss'Z'"),
        timeZone: 'UTC',
      },
      end: {
        dateTime: format(utcEndDate, "yyyy-MM-dd'T'HH:mm:ss'Z'"),
        timeZone: 'UTC',
      },
      reminders: {
        useDefault: false,
        overrides: [
          { method: 'popup', minutes: 30 },
        ],
      },
    };

    try {
      const response = await fetch('https://www.googleapis.com/calendar/v3/calendars/primary/events', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event),
      });

      if (!response.ok) {
        throw new Error('Failed to create calendar event');
      }

      const createdEvent = await response.json();
      return createdEvent;
    } catch (error) {
      console.error('Error creating calendar event:', error);
      throw error;
    }
  }
}

export const func = async ({ summary, startDateTime, endDateTime, description }: { summary: string; startDateTime: string; endDateTime?: string; description?: string }): Promise<string> => {
  const calendarManager = GoogleCalendarManager.getInstance();
  
  try {
    const authResponse = await fetch('https://scripty.me/api/assistant/google-auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scope: 'calendar' }),
    });

    if (!authResponse.ok) {
      throw new Error('Failed to initiate Google authentication');
    }

    const { authUrl, state } = await authResponse.json();

    const authResult = await new Promise<{tokens: any, state: string}>((resolve, reject) => {
      const authWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true
        }
      });

      authWindow.loadURL(authUrl);

      const handleCallback = (url: string) => {
        const urlParams = new URLSearchParams(url.split('?')[1]);
        const code = urlParams.get('code');
        const returnedState = urlParams.get('state');

        if (code && returnedState && returnedState === state) {
          authWindow.loadURL(`https://scripty.me/api/assistant/google/calendar-callback?code=${code}&state=${returnedState}`);
        } else {
          reject(new Error('Authentication failed: Invalid code or state'));
        }
      };

      authWindow.webContents.on('will-navigate', (event, url) => {
        if (url.startsWith('https://scripty.me/api/auth/google/callback')) {
          handleCallback(url);
        }
      });

      authWindow.webContents.on('did-navigate', (event, url) => {
        if (url.startsWith('https://scripty.me/api/assistant/google/calendar-callback')) {
          authWindow.webContents.executeJavaScript('document.body.innerHTML')
            .then(html => {
              const match = html.match(/window\.opener\.postMessage\(({.*}),/);
              if (match) {
                const data = JSON.parse(match[1]);
                resolve(data);
              } else {
                reject(new Error('Failed to extract tokens from response'));
              }
              authWindow.close();
            });
        }
      });

      authWindow.on('closed', () => {
        reject(new Error('Auth window was closed'));
      });
    });

    if (authResult.state !== state) {
      throw new Error('State mismatch. Possible security issue.');
    }

    const createdEvent = await calendarManager.createUserFriendlyReminder(
      { summary, startDateTime, endDateTime, description },
      authResult.tokens.access_token
    );

    return JSON.stringify({
      success: true,
      message: 'Reminder set successfully',
      event: createdEvent
    });

  } catch (error) {
    console.error('Error in set_calendar_reminder:', error);
    return JSON.stringify({
      success: false,
      error: `Error setting reminder: ${(error as Error).message}`
    });
  }
};

export const object = {
  name: 'set_calendar_reminder',
  description: 'Set a reminder in Google Calendar with user-friendly date/time input.',
  parameters: {
    type: 'object',
    properties: {
      summary: {
        type: 'string',
        description: 'The title or summary of the reminder'
      },
      startDateTime: {
        type: 'string',
        description: 'The start date and time of the reminder (e.g., "tomorrow 3pm", "next monday 10am", "2023-05-20 14:30")'
      },
      endDateTime: {
        type: 'string',
        description: 'The end date and time of the reminder (optional, defaults to 1 hour after start time)'
      },
      description: {
        type: 'string',
        description: 'Additional details or description for the reminder (optional)'
      }
    },
    required: ['summary', 'startDateTime']
  }
};
