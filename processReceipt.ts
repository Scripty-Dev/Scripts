import fs from 'fs';
import { createWorker } from 'tesseract.js';

interface Item {
  name: string;
  price: string;
}

interface DocumentInfo {
  type: 'invoice' | 'receipt';
  title: string;
  invoiceNumber: string;
  items: Item[];
  subtotal: string;
  date: string;
  total: string;
}

function parseDocument(text: string): DocumentInfo {
  const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
  const info: DocumentInfo = {
    type: 'receipt',
    title: '',
    invoiceNumber: '',
    items: [],
    subtotal: '',
    date: '',
    total: ''
  };

  // Determine document type and extract basic info
  if (text.toLowerCase().includes('invoice')) {
    info.type = 'invoice';
    info.title = extractCompanyName(lines);
    info.invoiceNumber = extractInvoiceNumber(lines);
  } else {
    info.type = 'receipt';
    info.title = extractStoreName(lines);
  }

  let itemsStarted = false;
  const itemRegex = /^(.+?)\s+\$?(\d+\.\d{2})\s*[DJP]?$/i;

  for (const line of lines) {
    // Extract date
    if (!info.date) {
      info.date = extractDate(line);
    }

    // Extract total
    if (line.toLowerCase().includes('total')) {
      const totalMatch = line.match(/(\d+\.\d{2})/);
      if (totalMatch) {
        info.total = totalMatch[1];
      }
    }

    // Extract subtotal
    if (line.toLowerCase().includes('subtotal')) {
      const subtotalMatch = line.match(/(\d+\.\d{2})/);
      if (subtotalMatch) {
        info.subtotal = subtotalMatch[1];
      }
    }

    // Extract items
    if (itemsStarted || line.match(/^\d{6,}/) || (info.type === 'invoice' && line.includes('$'))) {
      const match = line.match(itemRegex);
      if (match) {
        let itemName = match[1].trim();
        const price = match[2];

        itemName = itemName.replace(/\s+\d+(?:\s+\d+)*\s+/g, ' ').trim();

        info.items.push({
          name: itemName,
          price: price
        });
      }
    } else if (line.toLowerCase().includes('st#') || line.toLowerCase().includes('te#') || line.toLowerCase().includes('item')) {
      itemsStarted = true;
    }
  }

  return info;
}

function extractCompanyName(lines: string[]): string {
  // Simple heuristic: assume company name is in the first few lines
  for (let i = 0; i < Math.min(5, lines.length); i++) {
    if (lines[i].length > 3 && !lines[i].match(/invoice|payment|receipt/i)) {
      return lines[i];
    }
  }
  return '';
}

function extractStoreName(lines: string[]): string {
  const storeNameIndex = lines.findIndex(line => 
    line.toLowerCase().includes('walmart') || 
    line.toLowerCase().includes('store') || 
    line.toLowerCase().includes('market')
  );
  return storeNameIndex !== -1 ? lines[storeNameIndex] : '';
}

function extractInvoiceNumber(lines: string[]): string {
  const invoiceLineIndex = lines.findIndex(line => 
    line.toLowerCase().includes('invoice') && line.includes('#')
  );
  if (invoiceLineIndex !== -1) {
    const match = lines[invoiceLineIndex].match(/#\s*(\d+)/);
    return match ? match[1] : '';
  }
  return '';
}

function extractDate(line: string): string {
  const dateFormats = [
    /(\d{2}\/\d{2}\/\d{2,4})/,
    /(\d{2}\/\d{2}\/\d{2})\s+\d{2}:\d{2}:\d{2}/,
    /(\d{4}-\d{2}-\d{2})/,
    /(\w+ \d{1,2},? \d{4})/  // e.g., May 21, 2024
  ];
  for (const format of dateFormats) {
    const dateMatch = line.match(format);
    if (dateMatch) {
      return dateMatch[1];
    }
  }
  return '';
}

async function scanAndParseDocument(imagePath: string): Promise<[string, DocumentInfo]> {
  const worker = await createWorker('eng');
  try {
    const { data: { text } } = await worker.recognize(imagePath);
    return [text, parseDocument(text)];
  } finally {
    await worker.terminate();
  }
}

function documentInfoToCSV(info: DocumentInfo): string {
  const rows = info.items.map(item => 
    `${info.type},${info.title},${info.invoiceNumber},${item.name},${item.price},${info.date},${info.subtotal},${info.total}`
  );
  return rows.join('\n');
}


function ensureCSVHeaders(outputPath: string): void {
  if (!fs.existsSync(outputPath)) {
    const headers = 'Type,Store/Company,Invoice Number,Item,Price,Date,Subtotal,Total\n';
    fs.writeFileSync(outputPath, headers);
  }
}

function appendToCSV(outputPath: string, content: string): void {
  const fileExists = fs.existsSync(outputPath);
  const newContent = (fileExists ? '\n' : '') + content + '\n';
  fs.appendFileSync(outputPath, newContent);
}


async function processDocument(imagePath: string, outputPath: string): Promise<DocumentInfo> {
  const [rawText, documentInfo] = await scanAndParseDocument(imagePath);
  
  console.log('Raw OCR Text:');
  console.log('--------------------------------------------------');
  console.log(rawText);
  console.log('--------------------------------------------------');

  ensureCSVHeaders(outputPath);
  const csvContent = documentInfoToCSV(documentInfo);
  appendToCSV(outputPath, csvContent);
  console.log('Document processed and appended to CSV file successfully.');
  
  return documentInfo;
}

export const func = async ({ imagePath, outputPath }) => {
  try {
    const documentInfo = await processDocument(imagePath, outputPath);
    return JSON.stringify({
      success: true,
      message: 'Document processed and CSV file updated successfully.',
      documentInfo
    });
  } catch (error) {
    return JSON.stringify({
      success: false,
      error: `Error processing document: ${error.message}`
    });
  }
};

export const object = {
  name: 'bookkeeper',
  description: 'Process a receipt or invoice image, extract information, and append to a CSV file.',
  parameters: {
    type: 'object',
    properties: {
      imagePath: {
        type: 'string',
        description: 'The file path to the receipt or invoice image'
      },
      outputPath: {
        type: 'string',
        description: 'The file path where the output CSV should be updated'
      }
    },
    required: ['imagePath', 'outputPath']
  }
};
