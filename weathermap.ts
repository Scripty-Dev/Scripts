export const func = async ({ city, country, units = 'metric', lang }: { 
  city: string; 
  country: string;
  units?: 'standard' | 'metric' | 'imperial';
  lang?: string;
}): Promise<string> => {
  try {
    const weatherRequest = await fetch(`https://scripty.me/api/assistant/weathermap?token=${config['token']}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        city,
        country,
        units,
        lang
      }),
    });
    
    if (!weatherRequest.ok) {
      throw new Error(`HTTP error! status: ${weatherRequest.status}`);
    }
    
    const weatherResponse = await weatherRequest.json();
    return JSON.stringify(weatherResponse);
  } catch (error) {
    console.error('Error fetching weather data:', error);
    return JSON.stringify({ error: 'Failed to fetch weather data' });
  }
};

export const object = {
  name: 'weathermap',
  description: 'Get weather forecasts for a given location using OpenWeatherMap API free tier. Provides hourly forecast for today, 36-hour forecast, and weekly forecast.',
  parameters: {
    type: 'object',
    properties: {
      city: {
        type: 'string',
        description: 'Name of the city',
      },
      country: {
        type: 'string',
        description: 'Two-letter country code',
      },
      units: {
        type: 'string',
        description: 'Units of measurement (optional, defaults to metric)',
        enum: ['standard', 'metric', 'imperial'],
      },
      lang: {
        type: 'string',
        description: 'Language code for the weather description (optional)',
      },
    },
    required: ['city', 'country'],
  },
};
