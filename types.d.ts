import vm from 'vm'

declare global {
    const config: object
    function scriptContext(
        code: string,
        functions?: Function[]
    ): Promise<{ result: any; error: string | null }>
}

export {}
