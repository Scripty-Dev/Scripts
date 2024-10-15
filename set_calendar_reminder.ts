import { parseISO, addHours, addDays, addWeeks, startOfDay, format } from 'date-fns';
import { zonedTimeToUtc } from 'date-fns-tz';

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

    const utcStartDate = zonedTimeToUtc(startDate, this.timeZone);
    const utcEndDate = zonedTimeToUtc(endDate, this.timeZone);

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
    // Step 1: Initiate Google authentication
    const authResponse = await fetch('https://scripty.me/api/auth/google-auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scope: 'calendar' }),
    });

    if (!authResponse.ok) {
      throw new Error('Failed to initiate Google authentication');
    }

    const { authUrl } = await authResponse.json();
    
    window.open(authUrl, '_blank');

    // Step 2: Return the authUrl to the client
    return JSON.stringify({
      success: true,
      message: 'Authentication required',
      pendingAction: {
        type: 'set_calendar_reminder',
        details: { summary, startDateTime, endDateTime, description }
      }
    });

    // Note: The actual creation of the reminder will happen after the user completes authentication
    // and your application receives the token. You'll need to implement a way to handle this flow
    // in your main application logic.

  } catch (error) {
    return JSON.stringify({
      success: false,
      error: `Error setting reminder: ${(error as Error).message}`
    });
  }
};

export const object = {
  name: 'set_calendar_reminder',
  description: 'Initiate the process of setting a reminder in Google Calendar with user-friendly date/time input.',
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
