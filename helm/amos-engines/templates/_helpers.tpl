{{/*
AMOS Engines Helm Chart Helpers
*/}}

{{/* Expand the name of the chart */}}
{{- define "amos-engines.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Create chart name and version */}}
{{- define "amos-engines.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels */}}
{{- define "amos-engines.labels" -}}
helm.sh/chart: {{ include "amos-engines.chart" . }}
{{ include "amos-engines.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels */}}
{{- define "amos-engines.selectorLabels" -}}
app.kubernetes.io/name: {{ include "amos-engines.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Service account name */}}
{{- define "amos-engines.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "amos-engines.name" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* Image registry helper */}}
{{- define "amos-engines.image" -}}
{{- $registry := .Values.image.registry -}}
{{- $repository := .Values.image.repository -}}
{{- $tag := .Values.image.tag -}}
{{- printf "%s/%s:%s" $registry $repository $tag -}}
{{- end }}
