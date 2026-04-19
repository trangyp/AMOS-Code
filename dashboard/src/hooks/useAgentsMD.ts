/**
 * React Hook for AGENTS.md Management
 *
 * Provides state management and operations for AGENTS.md files.
 * Integrates with the AGENTS.md parser for validation and execution.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import {
  AGENTSFile,
  AGENTSValidationResult,
  AGENTSDiscoveryResult,
  AGENTSEditorState,
  parseAGENTSMD,
  validateAGENTSMD,
  generateTemplate,
  discoverAGENTSFiles,
  executeCommand
} from '../lib/agentsmd';

interface UseAgentsMDReturn {
  // State
  state: AGENTSEditorState;
  activeFile: AGENTSFile | null;
  activeValidation: AGENTSValidationResult | null;

  // File operations
  createFile: (projectType: 'web' | 'python' | 'node' | 'generic', name?: string) => void;
  loadFile: (content: string, filePath: string) => void;
  updateFile: (content: string) => void;
  saveFile: () => void;
  deleteFile: (fileId: string) => void;
  selectFile: (fileId: string) => void;

  // Discovery
  discoverFiles: (workspacePath: string) => Promise<AGENTSDiscoveryResult[]>;

  // Validation
  validateActive: () => AGENTSValidationResult;

  // Execution
  executeBuildCommand: (commandId: string) => Promise<{ success: boolean; output: string }>;

  // Templates
  applyTemplate: (projectType: 'web' | 'python' | 'node' | 'generic') => void;

  // Sections
  addSection: (title: string) => void;
  removeSection: (sectionId: string) => void;
  updateSection: (sectionId: string, content: string) => void;

  // Utilities
  exportToMarkdown: () => string;
  getQualityScore: () => number;
  getMissingSections: () => string[];
}

export function useAgentsMD(): UseAgentsMDReturn {
  // Editor state
  const [state, setState] = useState<AGENTSEditorState>({
    files: [],
    activeFileId: null,
    selectedSectionId: null,
    isEditing: false,
    hasChanges: false,
    validationResults: new Map()
  });

  // Derived state
  const activeFile = useMemo(() => {
    if (!state.activeFileId) return null;
    return state.files.find(f => f.id === state.activeFileId) || null;
  }, [state.files, state.activeFileId]);

  const activeValidation = useMemo(() => {
    if (!state.activeFileId) return null;
    return state.validationResults.get(state.activeFileId) || null;
  }, [state.validationResults, state.activeFileId]);

  // Create new AGENTS.md file
  const createFile = useCallback((projectType: 'web' | 'python' | 'node' | 'generic', name?: string) => {
    const template = generateTemplate(projectType);
    const parsed = parseAGENTSMD(template, name || 'AGENTS.md');
    const validation = validateAGENTSMD(parsed);

    setState(prev => ({
      ...prev,
      files: [...prev.files, parsed],
      activeFileId: parsed.id,
      hasChanges: true,
      validationResults: new Map(prev.validationResults).set(parsed.id, validation)
    }));
  }, []);

  // Load existing file
  const loadFile = useCallback((content: string, filePath: string) => {
    const parsed = parseAGENTSMD(content, filePath);
    const validation = validateAGENTSMD(parsed);

    setState(prev => {
      // Check if file already exists
      const existingIndex = prev.files.findIndex(f => f.filePath === filePath);
      let newFiles;

      if (existingIndex >= 0) {
        newFiles = [...prev.files];
        newFiles[existingIndex] = parsed;
      } else {
        newFiles = [...prev.files, parsed];
      }

      return {
        ...prev,
        files: newFiles,
        activeFileId: parsed.id,
        hasChanges: false,
        validationResults: new Map(prev.validationResults).set(parsed.id, validation)
      };
    });
  }, []);

  // Update active file content
  const updateFile = useCallback((content: string) => {
    if (!state.activeFileId) return;

    const file = state.files.find(f => f.id === state.activeFileId);
    if (!file) return;

    const parsed = parseAGENTSMD(content, file.filePath);
    const validation = validateAGENTSMD(parsed);

    setState(prev => {
      const newFiles = prev.files.map(f =>
        f.id === state.activeFileId ? parsed : f
      );

      return {
        ...prev,
        files: newFiles,
        hasChanges: true,
        validationResults: new Map(prev.validationResults).set(parsed.id, validation)
      };
    });
  }, [state.activeFileId, state.files]);

  // Save file (mark as saved)
  const saveFile = useCallback(() => {
    setState(prev => ({
      ...prev,
      hasChanges: false
    }));

    // In a real implementation, this would write to the file system
    console.log('Saving AGENTS.md file...', activeFile?.filePath);
  }, [activeFile]);

  // Delete file
  const deleteFile = useCallback((fileId: string) => {
    setState(prev => {
      const newFiles = prev.files.filter(f => f.id !== fileId);
      const newValidations = new Map(prev.validationResults);
      newValidations.delete(fileId);

      return {
        ...prev,
        files: newFiles,
        activeFileId: prev.activeFileId === fileId ? null : prev.activeFileId,
        validationResults: newValidations
      };
    });
  }, []);

  // Select active file
  const selectFile = useCallback((fileId: string) => {
    setState(prev => ({
      ...prev,
      activeFileId: fileId,
      selectedSectionId: null
    }));
  }, []);

  // Discover AGENTS.md files in workspace
  const discoverFiles = useCallback(async (workspacePath: string): Promise<AGENTSDiscoveryResult[]> => {
    const results = await discoverAGENTSFiles(workspacePath);

    // Load discovered files
    results.forEach(result => {
      if (result.found && result.parsed) {
        loadFile(result.parsed.content, result.path);
      }
    });

    return results;
  }, [loadFile]);

  // Validate active file
  const validateActive = useCallback((): AGENTSValidationResult => {
    if (!activeFile) {
      return {
        isValid: false,
        errors: ['No active file'],
        warnings: [],
        suggestions: [],
        score: 0,
        standardSections: [],
        missingStandardSections: []
      };
    }

    return validateAGENTSMD(activeFile);
  }, [activeFile]);

  // Execute build command
  const executeBuildCommand = useCallback(async (commandId: string): Promise<{ success: boolean; output: string }> => {
    if (!activeFile) return { success: false, output: 'No active file' };

    const buildSection = activeFile.sections.find(s => s.title === 'Build & Test');
    if (!buildSection?.parsedData?.commands) {
      return { success: false, output: 'No build commands found' };
    }

    const command = buildSection.parsedData.commands.find((c: any) => c.id === commandId);
    if (!command) return { success: false, output: 'Command not found' };

    const result = await executeCommand(command);
    return {
      success: result.success,
      output: result.output
    };
  }, [activeFile]);

  // Apply template to active file
  const applyTemplate = useCallback((projectType: 'web' | 'python' | 'node' | 'generic') => {
    const template = generateTemplate(projectType);
    updateFile(template);
  }, [updateFile]);

  // Add section
  const addSection = useCallback((title: string) => {
    if (!activeFile) return;

    const newContent = activeFile.content + `\n\n# ${title}\n\nAdd your ${title.toLowerCase()} instructions here...\n`;
    updateFile(newContent);
  }, [activeFile, updateFile]);

  // Remove section
  const removeSection = useCallback((sectionId: string) => {
    if (!activeFile) return;

    const sectionIndex = activeFile.sections.findIndex(s => s.id === sectionId);
    if (sectionIndex < 0) return;

    const section = activeFile.sections[sectionIndex];
    const lines = activeFile.content.split('\n');

    // Remove section lines
    const newLines = [
      ...lines.slice(0, section.lineStart - 1),
      ...lines.slice(section.lineEnd)
    ];

    updateFile(newLines.join('\n'));
  }, [activeFile, updateFile]);

  // Update section content
  const updateSection = useCallback((sectionId: string, content: string) => {
    if (!activeFile) return;

    const section = activeFile.sections.find(s => s.id === sectionId);
    if (!section) return;

    const lines = activeFile.content.split('\n');
    const newLines = [
      ...lines.slice(0, section.lineStart),
      ...content.split('\n'),
      ...lines.slice(section.lineEnd)
    ];

    updateFile(newLines.join('\n'));
  }, [activeFile, updateFile]);

  // Export to markdown
  const exportToMarkdown = useCallback((): string => {
    return activeFile?.content || '';
  }, [activeFile]);

  // Get quality score
  const getQualityScore = useCallback((): number => {
    return activeValidation?.score || 0;
  }, [activeValidation]);

  // Get missing standard sections
  const getMissingSections = useCallback((): string[] => {
    return activeValidation?.missingStandardSections || [];
  }, [activeValidation]);

  // Auto-validate on file change
  useEffect(() => {
    if (activeFile && !state.validationResults.has(activeFile.id)) {
      const validation = validateAGENTSMD(activeFile);
      setState(prev => ({
        ...prev,
        validationResults: new Map(prev.validationResults).set(activeFile.id, validation)
      }));
    }
  }, [activeFile, state.validationResults]);

  return {
    state,
    activeFile,
    activeValidation,
    createFile,
    loadFile,
    updateFile,
    saveFile,
    deleteFile,
    selectFile,
    discoverFiles,
    validateActive,
    executeBuildCommand,
    applyTemplate,
    addSection,
    removeSection,
    updateSection,
    exportToMarkdown,
    getQualityScore,
    getMissingSections
  };
}

export default useAgentsMD;
