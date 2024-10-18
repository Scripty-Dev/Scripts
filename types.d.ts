declare global {
    const config: {
        token: string
        [key: string]: any
    }
    const openUrl: (url: string) => void
    function scriptContext(
        code: string,
        functions?: Function[]
    ): Promise<{ result: any; error: string | null }>
}

export {}