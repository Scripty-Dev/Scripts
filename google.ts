export const func = async ({ query }: { query: string }) => {
    const request = await fetch('https://google.serper.dev/search', {
        method: 'POST',
        headers: {
            'X-API-KEY': config['serper-api-key'],
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            q: query,
        }),
    })

    const response = await request.json()
    return response.answerBox
        ? JSON.stringify(response.answerBox)
        : JSON.stringify(response.organic)
}

export const object = {
    name: 'google',
    description:
        'Search Google for the given query. The user is unable to see the search results, so you must tell the user the results.',
    parameters: {
        type: 'object',
        properties: {
            query: {
                type: 'string',
                description: 'The query to search for',
            },
        },
        required: ['query'],
    },
}
