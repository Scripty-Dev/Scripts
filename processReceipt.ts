const fs = require('fs')
const { createWorker } = require('tesseract.js')

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
}

function parseDocument(text: string): DocumentInfo {
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    const info: DocumentInfo = {
      type: 'receipt',
      title: '',
      invoiceNumber: '',
      items: [],
      subtotal: '',
      date: ''
    };
  
    // Extract store name (Walmart in this case)
    const storeNameIndex = lines.findIndex(line => line.toLowerCase().includes('walmart'));
    if (storeNameIndex !== -1) {
      info.title = 'Walmart';
    }
  
    let itemsStarted = false;
    const itemRegex = /^(.+?)\s+\$?(\d+\.\d{2})\s*[DJP]?$/i;
  
    for (const line of lines) {
      if (line.toLowerCase().includes('subtotal')) {
        const subtotalMatch = line.match(/(\d+\.\d{2})/);
        if (subtotalMatch) {
          info.subtotal = subtotalMatch[1];
        }
        break;
      }
  
      if (itemsStarted || line.match(/^\d{6,}/)) {
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
      } else if (line.toLowerCase().includes('st#') || line.toLowerCase().includes('te#')) {
        itemsStarted = true;
      }
    }

    // Extract date (trying multiple formats)
    const dateFormats = [
      /(\d{2}\/\d{2}\/\d{2,4})/,
      /(\d{2}\/\d{2}\/\d{2})\s+\d{2}:\d{2}:\d{2}/,
      /(\d{4}-\d{2}-\d{2})/
    ];

    for (const format of dateFormats) {
      const dateMatch = text.match(format);
      if (dateMatch) {
        info.date = dateMatch[1];
        break;
      }
    }

    return info;  // Return the parsed document info
}

async function scanAndParseDocument(imagePath: string): Promise<DocumentInfo> {
  const worker = await createWorker('eng');
  try {
    const { data: { text } } = await worker.recognize(imagePath);
    return parseDocument(text);
  } finally {
    await worker.terminate();
  }
}

function documentInfoToCSV(info: DocumentInfo): string {
  const headers = 'Store,Invoice Number,Item,Price,Date';
  const rows = info.items.map(item => 
    `${info.title},${info.invoiceNumber},${item.name},${item.price},${info.date}`
  );
  if (info.subtotal) {
    rows.push(`${info.title},${info.invoiceNumber},Subtotal,${info.subtotal},${info.date}`);
  }
  return [headers, ...rows].join('\n');
}

export const func = async ({ imagePath, outputPath }) => {
  try {
    const documentInfo = await scanAndParseDocument(imagePath);
    const csvContent = documentInfoToCSV(documentInfo);
    fs.writeFileSync(outputPath, csvContent);
    return JSON.stringify({
      success: true,
      message: 'Receipt processed and CSV file created successfully.',
      documentInfo
    });
  } catch (error) {
    return JSON.stringify({
      success: false,
      error: `Error processing receipt: ${error.message}`
    });
  }
};

export const object = {
  name: 'processReceipt',
  description: 'Process a receipt image, extract information, and create a CSV file.',
  parameters: {
    type: 'object',
    properties: {
      imagePath: {
        type: 'string',
        description: 'The file path to the receipt image'
      },
      outputPath: {
        type: 'string',
        description: 'The file path where the output CSV should be saved'
      }
    },
    required: ['imagePath', 'outputPath']
  }
};
