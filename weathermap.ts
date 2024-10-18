export const func = async ({ city, country, lat, lon }: { 
    city?: string; 
    country?: string; 
    lat?: number; 
    lon?: number; 
}): Promise<string> => {
    const request = await fetch('https://scripty.me/api/assistant/weathermap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            city,
            country,
            lat,
            lon,
            token: config['token'],
        }),
    });
    const response = await request.json();
    return JSON.stringify(response);
};

export const object = {
    name: 'weathermap',
    description: 'Get current weather data for a given location. You can provide either a city name (and optionally a country code), or latitude and longitude. If no location is provided, it will attempt to use the user\'s IP address for geolocation.',
    parameters: {
        type: 'object',
        properties: {
            city: {
                type: 'string',
                description: 'Name of the city',
            },
            country: {
                type: 'string',
                description: 'Two-letter country code (optional)',
            },
            lat: {
                type: 'number',
                description: 'Latitude of the location (optional)',
            },
            lon: {
                type: 'number',
                description: 'Longitude of the location (optional)',
            },
        },
    },
};