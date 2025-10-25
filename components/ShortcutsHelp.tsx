'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { X, Keyboard } from 'lucide-react';
import { KeyboardShortcut, formatShortcutKey } from '@/hooks/useKeyboardShortcuts';

interface ShortcutsHelpProps {
  shortcuts: KeyboardShortcut[];
  onClose: () => void;
}

export const ShortcutsHelp: React.FC<ShortcutsHelpProps> = ({ shortcuts, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto bg-popover backdrop-blur-sm shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Keyboard className="h-5 w-5" />
              Keyboard Shortcuts
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm text-foreground">{shortcut.description}</p>
                <Badge variant="secondary" className="font-mono text-xs px-3 py-1">
                  {formatShortcutKey(shortcut)}
                </Badge>
              </div>
            ))}
          </div>
          <div className="mt-6 p-3 bg-muted/50 border border-border rounded-lg">
            <p className="text-xs text-muted-foreground">
              <strong>Note:</strong> Shortcuts are disabled when typing in input fields. Press{' '}
              <kbd className="px-1.5 py-0.5 bg-background border border-border rounded text-xs font-mono">
                ?
              </kbd>{' '}
              to toggle this help panel.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
