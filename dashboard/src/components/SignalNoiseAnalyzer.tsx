/**
 * Signal-Noise Kernel Analyzer Component
 *
 * Real-time signal-noise separation for user input analysis.
 * Integrates with backend Signal-Noise Kernel API.
 *
 * Creator: Trang Phan
 * Version: 1.0.0
 */
import React, { useState, useCallback } from 'react';
import { useSignalNoise } from '../hooks';

interface SignalNoiseAnalyzerProps {
  onAnalysisComplete?: (result: SignalNoiseResult) => void;
}

interface SignalNoiseResult {
  input: string;
  signal_quality: number;
  noise_distortion: number;
  ambiguity_count: number;
  execution_safe: boolean;
  signals: Array<{
    signal_class: string;
    content: string;
    confidence: number;
  }>;
  noise_units: Array<{
    noise_class: string;
    content: string;
    distortion_score: number;
  }>;
  ambiguities: Array<{
    ambiguity_type: string;
    references: string[];
    severity: number;
  }>;
}

export const SignalNoiseAnalyzer: React.FC<SignalNoiseAnalyzerProps> = ({
  onAnalysisComplete,
}) => {
  const [input, setInput] = useState('');
  const { analyze, result, loading, error } = useSignalNoise();

  const handleAnalyze = useCallback(async () => {
    if (!input.trim()) return;

    const data = await analyze(input);
    if (onAnalysisComplete && data) {
      onAnalysisComplete(data as SignalNoiseResult);
    }
  }, [input, analyze, onAnalysisComplete]);

  const getSignalQualityColor = (quality: number) => {
    if (quality >= 0.8) return '#10b981';
    if (quality >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getNoiseDistortionColor = (distortion: number) => {
    if (distortion <= 0.2) return '#10b981';
    if (distortion <= 0.4) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={containerStyle}>
      <h3 style={titleStyle}>Signal-Noise Kernel Analyzer</h3>
      <p style={descriptionStyle}>
        Analyze text to separate signal (clear intent) from noise (distortion).
        Powered by AMOS Translation Layer.
      </p>

      <div style={inputSectionStyle}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter text to analyze..."
          style={textareaStyle}
          rows={4}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !input.trim()}
          style={{
            ...buttonStyle,
            opacity: loading || !input.trim() ? 0.6 : 1,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Analyzing...' : 'Analyze Signal-Noise'}
        </button>
      </div>

      {error && (
        <div style={errorStyle}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={resultsStyle}>
          <div style={metricsGridStyle}>
            <div style={metricCardStyle}>
              <div style={metricLabelStyle}>Signal Quality</div>
              <div
                style={{
                  ...metricValueStyle,
                  color: getSignalQualityColor(result.signal_quality),
                }}
              >
                {(result.signal_quality * 100).toFixed(0)}%
              </div>
              <div style={metricBarContainerStyle}>
                <div
                  style={{
                    ...metricBarStyle,
                    width: `${result.signal_quality * 100}%`,
                    backgroundColor: getSignalQualityColor(
                      result.signal_quality
                    ),
                  }}
                />
              </div>
            </div>

            <div style={metricCardStyle}>
              <div style={metricLabelStyle}>Noise Distortion</div>
              <div
                style={{
                  ...metricValueStyle,
                  color: getNoiseDistortionColor(result.noise_distortion),
                }}
              >
                {(result.noise_distortion * 100).toFixed(0)}%
              </div>
              <div style={metricBarContainerStyle}>
                <div
                  style={{
                    ...metricBarStyle,
                    width: `${result.noise_distortion * 100}%`,
                    backgroundColor: getNoiseDistortionColor(
                      result.noise_distortion
                    ),
                  }}
                />
              </div>
            </div>

            <div style={metricCardStyle}>
              <div style={metricLabelStyle}>Ambiguities</div>
              <div style={metricValueStyle}>{result.ambiguity_count}</div>
            </div>

            <div style={metricCardStyle}>
              <div style={metricLabelStyle}>Execution Safe</div>
              <div
                style={{
                  ...metricValueStyle,
                  color: result.execution_safe ? '#10b981' : '#ef4444',
                }}
              >
                {result.execution_safe ? 'Yes' : 'No'}
              </div>
            </div>
          </div>

          {result.signals.length > 0 && (
            <div style={sectionStyle}>
              <h4 style={sectionTitleStyle}>Extracted Signals</h4>
              {result.signals.map((signal, idx) => (
                <div key={idx} style={signalItemStyle}>
                  <span style={signalClassStyle}>{signal.signal_class}</span>
                  <span style={signalContentStyle}>{signal.content}</span>
                  <span style={signalConfidenceStyle}>
                    {(signal.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          )}

          {result.noise_units.length > 0 && (
            <div style={sectionStyle}>
              <h4 style={sectionTitleStyle}>Detected Noise</h4>
              {result.noise_units.map((noise, idx) => (
                <div key={idx} style={noiseItemStyle}>
                  <span style={noiseClassStyle}>{noise.noise_class}</span>
                  <span style={noiseContentStyle}>{noise.content}</span>
                  <span style={noiseSeverityStyle}>
                    {(noise.distortion_score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          )}

          {result.ambiguities.length > 0 && (
            <div style={sectionStyle}>
              <h4 style={sectionTitleStyle}>Ambiguities</h4>
              {result.ambiguities.map((ambiguity, idx) => (
                <div key={idx} style={ambiguityItemStyle}>
                  <span style={ambiguityTypeStyle}>
                    {ambiguity.ambiguity_type}
                  </span>
                  <span style={ambiguityRefsStyle}>
                    Refs: {ambiguity.references.join(', ')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Styles
const containerStyle: React.CSSProperties = {
  padding: '24px',
  backgroundColor: '#1e293b',
  borderRadius: '12px',
  color: '#f1f5f9',
  fontFamily: 'system-ui, -apple-system, sans-serif',
};

const titleStyle: React.CSSProperties = {
  margin: '0 0 8px 0',
  fontSize: '20px',
  fontWeight: 600,
};

const descriptionStyle: React.CSSProperties = {
  margin: '0 0 20px 0',
  fontSize: '14px',
  color: '#94a3b8',
};

const inputSectionStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  marginBottom: '20px',
};

const textareaStyle: React.CSSProperties = {
  padding: '12px',
  borderRadius: '8px',
  border: '1px solid #475569',
  backgroundColor: '#0f172a',
  color: '#f1f5f9',
  fontSize: '14px',
  resize: 'vertical',
};

const buttonStyle: React.CSSProperties = {
  padding: '12px 24px',
  backgroundColor: '#3b82f6',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  fontSize: '14px',
  fontWeight: 500,
  cursor: 'pointer',
  transition: 'background-color 0.2s',
};

const errorStyle: React.CSSProperties = {
  padding: '12px',
  backgroundColor: '#ef4444',
  color: 'white',
  borderRadius: '8px',
  marginBottom: '16px',
};

const resultsStyle: React.CSSProperties = {
  marginTop: '20px',
};

const metricsGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, 1fr)',
  gap: '16px',
  marginBottom: '24px',
};

const metricCardStyle: React.CSSProperties = {
  backgroundColor: '#0f172a',
  padding: '16px',
  borderRadius: '8px',
  textAlign: 'center',
};

const metricLabelStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#94a3b8',
  marginBottom: '8px',
  textTransform: 'uppercase',
};

const metricValueStyle: React.CSSProperties = {
  fontSize: '24px',
  fontWeight: 700,
  marginBottom: '8px',
};

const metricBarContainerStyle: React.CSSProperties = {
  height: '4px',
  backgroundColor: '#334155',
  borderRadius: '2px',
  overflow: 'hidden',
};

const metricBarStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '2px',
  transition: 'width 0.3s ease',
};

const sectionStyle: React.CSSProperties = {
  marginTop: '20px',
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  marginBottom: '12px',
  color: '#e2e8f0',
};

const signalItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  padding: '8px 12px',
  backgroundColor: '#0f172a',
  borderRadius: '6px',
  marginBottom: '8px',
  borderLeft: '3px solid #10b981',
};

const signalClassStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  color: '#10b981',
  textTransform: 'uppercase',
  minWidth: '120px',
};

const signalContentStyle: React.CSSProperties = {
  flex: 1,
  fontSize: '14px',
};

const signalConfidenceStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#94a3b8',
};

const noiseItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  padding: '8px 12px',
  backgroundColor: '#0f172a',
  borderRadius: '6px',
  marginBottom: '8px',
  borderLeft: '3px solid #f59e0b',
};

const noiseClassStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  color: '#f59e0b',
  textTransform: 'uppercase',
  minWidth: '120px',
};

const noiseContentStyle: React.CSSProperties = {
  flex: 1,
  fontSize: '14px',
};

const noiseSeverityStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#94a3b8',
};

const ambiguityItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  padding: '8px 12px',
  backgroundColor: '#0f172a',
  borderRadius: '6px',
  marginBottom: '8px',
  borderLeft: '3px solid #ef4444',
};

const ambiguityTypeStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  color: '#ef4444',
  textTransform: 'uppercase',
  minWidth: '120px',
};

const ambiguityRefsStyle: React.CSSProperties = {
  flex: 1,
  fontSize: '14px',
  color: '#94a3b8',
};
