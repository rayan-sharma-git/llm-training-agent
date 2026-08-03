import { describe, it, expect } from 'vitest';
import { formatError, generateReportHtml } from '../../src/utils';

describe('formatError', () => {
  it('should format Error instances', () => {
    expect(formatError(new Error('broken'))).toBe('broken');
  });

  it('should format strings', () => {
    expect(formatError('string error')).toBe('string error');
  });

  it('should coerce unknown values to string', () => {
    expect(formatError(123)).toBe('123');
    expect(formatError(null)).toBe('null');
  });
});

describe('generateReportHtml', () => {
  it('should generate basic HTML for object reports', () => {
    const report = { summary: 'ok', items: [1, 2] };
    const html = generateReportHtml(report);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('Analysis Report');
    expect(html).toContain('"summary": "ok"');
    expect(html).toContain('<pre>');
  });

  it('should allow string reports without JSON.stringify', () => {
    const html = generateReportHtml('<b>raw</b>');
    expect(html).toContain('<b>raw</b>');
  });
});