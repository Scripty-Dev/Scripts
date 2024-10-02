const fs = require('fs')
const csvParser = require('csv-parser')

const parseCSV = (filePath: string, options: any = {}): Promise<any[]> =>
    new Promise((resolve, reject) => {
        const results: any[] = []
        fs.createReadStream(filePath)
            .pipe(csvParser(options))
            .on('data', (data: Record<string, unknown>) => results.push(data))
            .on('end', () => resolve(results))
            .on('error', (error: Error) => reject(error))
    })

const writeCSV = (data: any[], filePath: string) => {
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map((row) => Object.values(row).join(','))
    const csvContent = [headers, ...rows].join('\n')

    fs.writeFileSync(filePath, csvContent)
}

const editColumnByNumber = (
    data: any[],
    columnIndex: number,
    editFunction: (value: string) => string
): any[] =>
    data.map((row) => {
        const newRow = { ...row }
        const columns = Object.keys(newRow)
        if (columnIndex >= 0 && columnIndex < columns.length) {
            const columnName = columns[columnIndex]
            const editedValue = editFunction(newRow[columnName])
            if (editedValue === '') delete newRow[columnName]
            else newRow[columnName] = editedValue
        }

        return newRow
    })

export const func = async ({ code }: { code: string }) => {
    const { result, error } = await scriptContext(code, [
        parseCSV,
        editColumnByNumber,
        writeCSV,
    ])

    if (error) {
        console.error(`Error executing script: ${error}`)
        return `Error executing script: ${error}`
    }

    return JSON.stringify(result) === '{}'
        ? 'No data was returned'
        : JSON.stringify(result)
}

export const object = {
    name: 'dataManipulation',
    description: `Execute TypeScript code to make versions of files with formatted data as specified by the user. Avoid manipulating the data of the original file by creating a new file. This module provides two main functions:

1. parseCSV(filePath: string, options?: csvParser.Options): Promise<any[]>
Parses a CSV file and returns a Promise that resolves to an array of objects. Each object represents a row in the CSV.
Usage: const data = await parseCSV('path/to/file.csv')

2. writeCSV(data: any[], filePath: string): void
Writes the provided data array to a CSV file at the specified file path.
Usage: writeCSV(editedData, 'path/to/output.csv')

3. editColumnByNumber(data: any[], columnIndex: number, editFunction: (value: string) => string): any[]
Edits a specific column in the parsed CSV data.
Usage: const editedData = editColumnByNumber(data, 1, (value) => value.toUpperCase())

These functions can be used together to parse and manipulate CSV data.`,
    parameters: {
        type: 'object',
        properties: {
            code: {
                type: 'string',
                description: 'The TypeScript code to execute',
            },
        },
        required: ['code'],
    },
}
