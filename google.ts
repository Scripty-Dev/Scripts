export const func = async ({ query }: { query: string }) => {
    const request = await fetch('https://scripty.me/api/assistant/serper', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            token: config['token'],
        }),
    })

    const response = await request.json()
    return response
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
