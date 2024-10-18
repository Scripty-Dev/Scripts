export const func = async ({ city, country }: { 
    city?: string; 
    country?: string; 
}): Promise<string> => {
    const request = await fetch('https://scripty.me/api/assistant/weathermap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            city,
            country,
            token: config['token'],
        }),
    });
    const response = await request.json();
    return JSON.stringify(response);
};

export const object = {
    name: 'weathermap',
    description: 'Get current weather data for a given location. Provide a city name, and optionally a country code. If no location is provided, it will attempt to use the user\'s IP address for geolocation.',
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
        },
    },
};
