export const func = async ({ city, country }: { 
    city?: string; 
    country?: string; 
}): Promise<string> => {
    let lat, lon;

    if (city) {
        // Use the 'google' function to geocode the city and country
        const query = country ? `${city}, ${country}` : city;
        const geocodeResult = await google({ query: `coordinates of ${query}` });
        const geocodeData = JSON.parse(geocodeResult);

        // Extract latitude and longitude from the geocode result
        // This is a simplified example; you may need to adjust based on the actual structure of the geocode result
        if (geocodeData.organic && geocodeData.organic[0] && geocodeData.organic[0].coordinates) {
            [lat, lon] = geocodeData.organic[0].coordinates.split(',').map(Number);
        } else {
            return JSON.stringify({ error: 'Unable to geocode the provided location' });
        }
    }

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
        }),
    });
    const weatherResponse = await weatherRequest.json();
    return JSON.stringify(weatherResponse);
};

export const object = {
    name: 'weathermap',
    description: 'Get current weather data for a given location. Provide a city name, and optionally a country code. The function will geocode the location and fetch the weather data.',
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
