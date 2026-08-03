import { describe, it, expect } from 'vitest';
import { formatError } from '../../src/utils';

describe('settings-like behavior', () => {
  it('should demonstrate error formatting', () => {
    expect(formatError(new Error('fail'))).toBe('fail');
    expect(formatError('plain')).toBe('plain');
    expect(formatError(123)).toBe('123');
  });
});