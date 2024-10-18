export const func = async () => {
    const request = await fetch('https://scripty.me/api/assistant/google/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            scopes: ['calendar'],
        }),
    })

    const response = await request.json()
    openUrl(response.url)
}

export const object = {
    name: 'calendar',
    description: 'Authenticate and test Google Calendar connection.',
    parameters: {
        type: 'object',
        properties: {},
        required: [],
    },
}