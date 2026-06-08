// @ts-ignore
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf';

export interface Rule {
  name: string;
  condition: string; // JavaScript expression to evaluate with keypoints and angle()
}

/**
 * Simple PDF rule extractor.
 * Loads the PDF from a public URL, extracts text, and creates dummy rule objects.
 * In a real implementation you would parse the actual rule format.
 */
export default class RuleExtractor {
  private url: string;

  constructor(pdfUrl: string) {
    this.url = pdfUrl;
    // Set worker src (pdfjs-dist provides a default worker script)
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
  }

  async extract(): Promise<Rule[]> {
    try {
      const loadingTask = pdfjsLib.getDocument(this.url);
      const pdf = await loadingTask.promise;
      const maxPages = pdf.numPages;
      let fullText = '';

      for (let pageNum = 1; pageNum <= maxPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const txt = await page.getTextContent();
        const pageText = txt.items.map((item: any) => (item.str as string)).join(' ');
        fullText += pageText + '\n';
      }

      // Very naive rule extraction: any line that starts with a number and a dot is considered a rule.
      const lines = fullText.split(/\n/);
      const rules: Rule[] = [];
      for (const line of lines) {
        const trimmed = line.trim();
        const match = /^\d+\.\s*(.+)$/.exec(trimmed);
        if (match) {
          const name = match[1];
          // Placeholder condition – real parsing would be needed.
          const condition = 'angle(keypoints[5], keypoints[7], keypoints[9]) < 30';
          rules.push({ name, condition });
        }
      }
      // Fallback: if no rules detected, return a generic rule.
      if (rules.length === 0) {
        rules.push({
          name: 'Default posture rule',
          condition: 'angle(keypoints[5], keypoints[7], keypoints[9]) < 30',
        });
      }
      return rules;
    } catch (e) {
      console.error('Error extracting PDF rules:', e);
      // Return a default rule on failure to keep the app functional.
      return [
        {
          name: 'Default posture rule',
          condition: 'angle(keypoints[5], keypoints[7], keypoints[9]) < 30',
        },
      ];
    }
  }
}
