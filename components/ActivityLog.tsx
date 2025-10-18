'use client';

import React, { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useBotStore } from '@/store/botStore';
import { LogLevel } from '@/types/bot';
import { formatTime } from '@/utils/formatters';
import {
  Download,
  Trash2,
  ArrowDown,
  ArrowDownToLine,
  FileText,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const LOG_FILTERS: (LogLevel | 'ALL')[] = ['ALL', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'TELEGRAM'];

export const ActivityLog: React.FC = () => {
  const activityLogs = useBotStore((state) => state.activityLogs);
  const clearLogs = useBotStore((state) => state.clearLogs);

  const [activeFilter, setActiveFilter] = useState<LogLevel | 'ALL'>('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll effect
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [activityLogs, autoScroll]);

  const filteredLogs = activityLogs.filter((log) =>
    activeFilter === 'ALL' ? true : log.level === activeFilter
  );

  const handleExportCSV = () => {
    const csv = [
      ['Timestamp', 'Level', 'Message', 'Bot ID'],
      ...filteredLogs.map((log) => [
        log.timestamp.toISOString(),
        log.level,
        log.message,
        log.botId || '',
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `activity-log-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Logs exported to CSV');
  };

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear all logs?')) {
      clearLogs();
      toast.success('All logs cleared');
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          {/* Tabs */}
          <div className="flex gap-2 flex-wrap">
            {LOG_FILTERS.map((filter) => {
              const count = filter === 'ALL' ? activityLogs.length : activityLogs.filter((l) => l.level === filter).length;
              return (
                <Button
                  key={filter}
                  variant={activeFilter === filter ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter(filter)}
                  className="h-8"
                >
                  {filter}
                  <Badge variant="secondary" className="ml-2 px-1.5 py-0">
                    {count}
                  </Badge>
                </Button>
              );
            })}
          </div>

          {/* Toolbar */}
          <div className="flex gap-2">
            <Button
              variant={autoScroll ? 'default' : 'outline'}
              size="sm"
              onClick={() => setAutoScroll(!autoScroll)}
              className="h-8"
              title="Auto-scroll"
            >
              {autoScroll ? <ArrowDownToLine className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportCSV} className="h-8">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="destructive" size="sm" onClick={handleClear} className="h-8">
              <Trash2 className="mr-2 h-4 w-4" />
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto" ref={logContainerRef}>
        {filteredLogs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No activity logs</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1 font-mono text-sm">
            {filteredLogs.map((log) => (
              <LogEntry key={log.id} log={log} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface LogEntryProps {
  log: {
    id: string;
    timestamp: Date;
    level: LogLevel;
    message: string;
    botId?: string;
  };
}

const LogEntry: React.FC<LogEntryProps> = ({ log }) => {
  const levelColors: Record<LogLevel, string> = {
    INFO: 'text-blue-400',
    SUCCESS: 'text-green-400',
    WARNING: 'text-yellow-400',
    ERROR: 'text-destructive',
    TELEGRAM: 'text-purple-400',
  };

  const levelBgColors: Record<LogLevel, string> = {
    INFO: 'bg-blue-500/10',
    SUCCESS: 'bg-green-500/10',
    WARNING: 'bg-yellow-500/10',
    ERROR: 'bg-destructive/10',
    TELEGRAM: 'bg-purple-500/10',
  };

  return (
    <div
      className={cn(
        'px-3 py-2 rounded hover:bg-opacity-20 transition-colors',
        levelBgColors[log.level]
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-muted-foreground whitespace-nowrap">
          {formatTime(log.timestamp)}
        </span>
        <span
          className={cn(
            levelColors[log.level],
            'font-semibold uppercase min-w-[70px] whitespace-nowrap'
          )}
        >
          {log.level}
        </span>
        <span className="text-foreground flex-1">{log.message}</span>
      </div>
    </div>
  );
};
