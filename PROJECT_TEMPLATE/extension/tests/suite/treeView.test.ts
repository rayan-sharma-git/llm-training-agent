import { describe, it, expect, vi } from 'vitest';
import * as vscode from 'vscode';
import { SimpleTreeDataProvider, registerTreeView } from '../../src/views/simpleTreeView';
import { ExtensionContext } from 'vscode';

vi.mock('vscode');

describe('SimpleTreeDataProvider', () => {
  it('should return entries', () => {
    const provider = new SimpleTreeDataProvider([
      { label: 'A' },
      { label: 'B' },
    ]);

    const items = provider.getChildren();
    expect(items?.length).toBe(2);
    expect(items?.[0].label).toBe('A');
    expect(items?.[1].label).toBe('B');
  });

  it('should return fallback when empty', () => {
    const provider = new SimpleTreeDataProvider([]);
    const items = provider.getChildren();
    expect(items?.length).toBe(1);
    expect(items?.[0].label).toBe('No data available');
  });

  it('should refresh entries', () => {
    const provider = new SimpleTreeDataProvider([]);
    provider.refresh([{ label: 'New' }]);
    const items = provider.getChildren();
    expect(items?.length).toBe(1);
    expect(items?.[0].label).toBe('New');
  });

  it('should pass commands to TreeItem', () => {
    const provider = new SimpleTreeDataProvider([
      {
        label: 'Run',
        command: { command: 'cmd', title: 'Run' },
      },
    ]);
    const items = provider.getChildren();
    expect(items?.[0].command?.command).toBe('cmd');
  });
});

describe('registerTreeView', () => {
  it('should register a provider and return it', () => {
    const mockContext = {
      subscriptions: [],
    } as unknown as ExtensionContext;

    const provider = registerTreeView(mockContext, 'test', [{ label: 'X' }]);
    expect(provider).toBeInstanceOf(SimpleTreeDataProvider);
  });
});