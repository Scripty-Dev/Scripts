export const func = async ({ city, country }: { 
  city?: string; 
  country?: string; 
}): Promise<string> => {
  if (!city) {
    return JSON.stringify({ error: 'City is required' });
  }

  const coordinates = await geocode(city, country);
  if (!coordinates) {
    return JSON.stringify({ error: 'Unable to geocode the provided location' });
  }

  const [lat, lon] = coordinates;
  
  // Make the weather request with lat and lon
  const weatherRequest = await fetch('https://scripty.me/api/assistant/weathermap', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      lat,
      lon,
      token: config['token'],
      units: 'metric', // You can make this configurable
    }),
  });
  const weatherResponse = await weatherRequest.json();
  return JSON.stringify(weatherResponse);
};

export const object = {
  name: 'weathermap',
  description: 'Get current weather data for a given location using OpenWeatherMap One Call API 3.0. Provide a city name and country code. The function will geocode the location using OpenWeatherMap\'s geocoding API and fetch the weather data.',
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
