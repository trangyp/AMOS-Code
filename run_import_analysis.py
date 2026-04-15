#!/usr/bin/env python3
"""
Run Import Analysis on AMOS codebase.
Executes the Import Analyzer and displays results.
"""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from repo_doctor.import_analyzer import ImportAnalyzer, DependencyGraph

print('=' * 70)
print('IMPORT DEPENDENCY ANALYSIS - AMOS CODEBASE')
print('=' * 70)

analyzer = ImportAnalyzer('.')

# Find Python files (limited subset for speed)
py_files = []
for root, dirs, files in Path('.').rglob('*.py'):
    if '__pycache__' not in str(root) and '.venv' not in str(root):
        py_files.extend([Path(root) / f for f in files])
        if len(py_files) >= 50:
            break

print(f'\nAnalyzing {len(py_files)} Python files...')

# Build mini dependency graph
graph = DependencyGraph()
for filepath in py_files:
    if filepath.exists():
        try:
            imports = analyzer._extract_imports(filepath)
            module_name = str(filepath.with_suffix('')).replace('/', '.')
            for imp in imports:
                imported = imp.imported_module
                if imp.is_relative:
                    base = '.'.join(module_name.split('.')[:-1])
                    imported = f"{base}.{imported}" if imported else base
                graph.add_edge(module_name, imported)
        except Exception as e:
            pass

print(f'\n✓ Graph built: {len(graph.vertices)} vertices, {len(graph.edges)} edges')

# Find cycles
cycles = analyzer.find_cycles(graph)
print(f'✓ Cycles found: {len(cycles)}')

# Calculate metrics
metrics = analyzer.calculate_coupling_metrics(graph)
print(f'✓ Metrics calculated for {len(metrics)} modules')

# Show most unstable modules
if metrics:
    sorted_metrics = sorted(metrics.values(), key=lambda m: m.efferent_coupling, reverse=True)
    print('\nMost Unstable Modules (high efferent coupling):')
    for m in sorted_metrics[:5]:
        print(f'  {m.module[:50]:50s}: Eff={m.efferent_coupling:2d}, Aff={m.afferent_coupling:2d}, I={m.instability:.2f}')

# Show cycles
if cycles:
    print('\nCircular Dependencies:')
    for i, cycle in enumerate(cycles[:3], 1):
        print(f'  {i}. {" -> ".join(cycle)}')

print('\n' + '=' * 70)
print('ANALYSIS COMPLETE')
print('=' * 70)
print(f'\nTotal modules analyzed: {len(graph.vertices)}')
print(f'Total dependencies: {len(graph.edges)}')
print(f'Circular dependencies: {len(cycles)}')
