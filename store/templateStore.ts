import { create } from 'zustand';
import { BotFormData } from '@/types/bot';

export interface BotTemplate {
  id: string;
  name: string;
  description?: string;
  config: BotFormData;
  createdAt: Date;
  updatedAt: Date;
}

interface TemplateStore {
  // State
  templates: BotTemplate[];

  // Actions
  addTemplate: (name: string, config: BotFormData, description?: string) => void;
  removeTemplate: (id: string) => void;
  updateTemplate: (id: string, updates: Partial<BotTemplate>) => void;
  loadTemplates: () => void;
  applyTemplate: (templateId: string) => BotFormData | null;
}

const STORAGE_KEY = 'bot_templates';

// Helper to load templates from localStorage
const loadFromStorage = (): BotTemplate[] => {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const parsed = JSON.parse(stored);
    return parsed.map((t: any) => ({
      ...t,
      createdAt: new Date(t.createdAt),
      updatedAt: new Date(t.updatedAt),
    }));
  } catch (error) {
    console.error('Failed to load templates from storage:', error);
    return [];
  }
};

// Helper to save templates to localStorage
const saveToStorage = (templates: BotTemplate[]) => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
  } catch (error) {
    console.error('Failed to save templates to storage:', error);
  }
};

// Helper to generate ID
const generateId = () => {
  return `tmpl_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

export const useTemplateStore = create<TemplateStore>((set, get) => ({
  // Initial state
  templates: loadFromStorage(),

  // Add new template
  addTemplate: (name: string, config: BotFormData, description?: string) => {
    const newTemplate: BotTemplate = {
      id: generateId(),
      name,
      description,
      config,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    set((state) => {
      const updated = [...state.templates, newTemplate];
      saveToStorage(updated);
      return { templates: updated };
    });
  },

  // Remove template
  removeTemplate: (id: string) => {
    set((state) => {
      const updated = state.templates.filter((t) => t.id !== id);
      saveToStorage(updated);
      return { templates: updated };
    });
  },

  // Update template
  updateTemplate: (id: string, updates: Partial<BotTemplate>) => {
    set((state) => {
      const updated = state.templates.map((t) =>
        t.id === id
          ? { ...t, ...updates, updatedAt: new Date() }
          : t
      );
      saveToStorage(updated);
      return { templates: updated };
    });
  },

  // Load templates from storage
  loadTemplates: () => {
    set({ templates: loadFromStorage() });
  },

  // Apply template (returns config)
  applyTemplate: (templateId: string) => {
    const template = get().templates.find((t) => t.id === templateId);
    return template ? { ...template.config } : null;
  },
}));
