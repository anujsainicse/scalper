'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useTemplateStore, BotTemplate } from '@/store/templateStore';
import { BotFormData } from '@/types/bot';
import toast from 'react-hot-toast';
import { Save, Trash2, FileCheck, Clock, Edit3, X } from 'lucide-react';
import { formatRelativeTime } from '@/utils/formatters';

interface BotTemplatesProps {
  currentConfig?: BotFormData;
  onApplyTemplate: (config: BotFormData) => void;
  onClose?: () => void;
}

export const BotTemplates: React.FC<BotTemplatesProps> = ({
  currentConfig,
  onApplyTemplate,
  onClose,
}) => {
  const templates = useTemplateStore((state) => state.templates);
  const addTemplate = useTemplateStore((state) => state.addTemplate);
  const removeTemplate = useTemplateStore((state) => state.removeTemplate);
  const updateTemplate = useTemplateStore((state) => state.updateTemplate);
  const applyTemplate = useTemplateStore((state) => state.applyTemplate);

  const [isCreating, setIsCreating] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplateDesc, setNewTemplateDesc] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');

  const handleSaveTemplate = () => {
    if (!currentConfig) {
      toast.error('No configuration to save');
      return;
    }

    if (!newTemplateName.trim()) {
      toast.error('Template name is required');
      return;
    }

    addTemplate(newTemplateName.trim(), currentConfig, newTemplateDesc.trim() || undefined);
    toast.success(`✅ Template "${newTemplateName}" saved`);
    setNewTemplateName('');
    setNewTemplateDesc('');
    setIsCreating(false);
  };

  const handleApplyTemplate = (templateId: string) => {
    const config = applyTemplate(templateId);
    if (config) {
      onApplyTemplate(config);
      const template = templates.find((t) => t.id === templateId);
      toast.success(`✅ Applied template "${template?.name}"`);
      if (onClose) onClose();
    } else {
      toast.error('Failed to apply template');
    }
  };

  const handleDeleteTemplate = (id: string, name: string) => {
    if (window.confirm(`Delete template "${name}"?`)) {
      removeTemplate(id);
      toast.success(`🗑️ Template deleted`);
    }
  };

  const handleStartEdit = (template: BotTemplate) => {
    setEditingId(template.id);
    setEditName(template.name);
    setEditDesc(template.description || '');
  };

  const handleSaveEdit = (id: string) => {
    if (!editName.trim()) {
      toast.error('Template name is required');
      return;
    }

    updateTemplate(id, {
      name: editName.trim(),
      description: editDesc.trim() || undefined,
    });

    toast.success('✅ Template updated');
    setEditingId(null);
    setEditName('');
    setEditDesc('');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditName('');
    setEditDesc('');
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileCheck className="h-5 w-5" />
            Bot Templates
            <Badge variant="secondary" className="ml-2">
              {templates.length}
            </Badge>
          </CardTitle>
          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Save Current Config */}
        {currentConfig && (
          <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 rounded-lg">
            {!isCreating ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-700 dark:text-blue-400">
                    Save Current Configuration
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Create a template from your current bot settings
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={() => setIsCreating(true)}
                  className="bg-blue-600 hover:bg-blue-500 text-white"
                >
                  <Save className="mr-1.5 h-3.5 w-3.5" />
                  Save as Template
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-blue-700 dark:text-blue-400 block mb-1">
                    Template Name *
                  </label>
                  <input
                    type="text"
                    value={newTemplateName}
                    onChange={(e) => setNewTemplateName(e.target.value)}
                    placeholder="e.g., BTC Scalping Strategy"
                    className="w-full px-3 py-2 text-sm border border-blue-300 dark:border-blue-500/40 rounded bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-blue-700 dark:text-blue-400 block mb-1">
                    Description (Optional)
                  </label>
                  <textarea
                    value={newTemplateDesc}
                    onChange={(e) => setNewTemplateDesc(e.target.value)}
                    placeholder="Brief description of this strategy..."
                    rows={2}
                    className="w-full px-3 py-2 text-sm border border-blue-300 dark:border-blue-500/40 rounded bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={handleSaveTemplate}
                    className="bg-blue-600 hover:bg-blue-500 text-white"
                  >
                    <Save className="mr-1.5 h-3.5 w-3.5" />
                    Save Template
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setIsCreating(false);
                      setNewTemplateName('');
                      setNewTemplateDesc('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Templates List */}
        {templates.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FileCheck className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No templates saved yet</p>
            <p className="text-xs mt-1">Save your bot configurations for quick reuse</p>
          </div>
        ) : (
          <div className="space-y-2">
            {templates.map((template) => (
              <div
                key={template.id}
                className="p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                {editingId === template.id ? (
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <textarea
                      value={editDesc}
                      onChange={(e) => setEditDesc(e.target.value)}
                      placeholder="Description..."
                      rows={2}
                      className="w-full px-2 py-1 text-sm border border-border rounded bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleSaveEdit(template.id)}
                        className="h-7 text-xs"
                      >
                        Save
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleCancelEdit}
                        className="h-7 text-xs"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm">{template.name}</h4>
                        {template.description && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {template.description}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-1 ml-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleStartEdit(template)}
                          className="h-7 w-7 p-0"
                          title="Edit"
                        >
                          <Edit3 className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteTemplate(template.id, template.name)}
                          className="h-7 w-7 p-0 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-500/10"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{template.config.ticker}</span>
                        <span>•</span>
                        <span>{template.config.exchange}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatRelativeTime(template.createdAt)}
                        </span>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleApplyTemplate(template.id)}
                        className="h-7 text-xs bg-green-600 hover:bg-green-500 text-white"
                      >
                        <FileCheck className="mr-1 h-3 w-3" />
                        Apply
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
