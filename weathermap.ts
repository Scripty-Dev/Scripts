export const func = async ({ city, country }: { 
  city: string; 
  country: string; 
}): Promise<string> => {
  try {
    const weatherRequest = await fetch('https://scripty.me/api/assistant/weathermap', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        city,
        country,
        token: config['token'],
        units: 'metric', // You can make this configurable if needed
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
  description: 'Get current weather data for a given location using OpenWeatherMap API. Provide a city name and country code.',
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
    },
    required: ['city', 'country'],
  },
};
